import sys
from io import StringIO

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

UNDEF = object()


class ParserError(Exception):
    pass


class YamlLoaderBase(type):
    def __init__(cls, name, bases, attrs):
        cls.__abstract__ = attrs.get("__abstract__", False)
        if not cls.__abstract__:
            cls.__yaml_name__ = attrs.get("__yaml_name__", name.lower())
            type(cls).registry[cls.__yaml_name__] = cls


class YamlLoader:
    def __init__(self, **kwargs):
        self.__fields__ = {}
        self.__lazy_fields__ = {}
        cls = type(self)
        for k, v in kwargs.items():
            if k in self._lazy_fields():
                self.__lazy_fields__[k] = v
                continue
            if k not in self._fields():
                raise ParserError("unknown field for %s: `%s`" % (
                    cls.__yaml_name__, k))
            setattr(self, k, v)

    @classmethod
    def _fields(cls):
        return [name
                for name in dir(cls)
                if isinstance(getattr(cls, name), YamlField)]

    @classmethod
    def _lazy_fields(cls):
        return [name
                for name in dir(cls)
                if isinstance(getattr(cls, name), LazyYamlField)]

    @classmethod
    def _main_list_field(cls):
        for name in cls._fields():
            f = getattr(cls, name)
            if isinstance(f, ArrayField) and f.is_main:
                return name

    @classmethod
    def _main_scalar_field(cls):
        for name in cls._fields():
            f = getattr(cls, name)
            if isinstance(f, ScalarField) and f.is_main:
                return name

    @classmethod
    def _factory(cls, data):
        name, spec = list(data.items())[0]
        try:
            loader_class = type(cls).registry[name]
        except KeyError:
            raise ValueError("No %s named `%s` found." % (type(cls).type_name,
                                                          name))
        if isinstance(spec, dict):
            return loader_class(**spec)
        elif isinstance(spec, list):
            main = loader_class._main_list_field()
            if main is None:
                raise ValueError("%s `%s` expects a mapping. Got a list.")
            return loader_class(**{main: spec})
        else:
            main = loader_class._main_scalar_field()
            if main is None:
                raise ValueError("%s `%s` expects a mapping. Got a scalar.")
            return loader_class(**{main: spec})

    @classmethod
    def scaffold(cls, comments=False, indent=0, out=None):
        scaffolder = YamlLoaderScaffolder(comments=comments)
        scaffolder.visit(cls)
        if out is None:
            out = sys.stdout
        return scaffolder.dump(out)



class YamlField:
    ord_gen = iter(range(99999999))

    def __init__(self, help=None, default=UNDEF, is_main=False, choice=None):
        self.help = help
        self.default = default
        self.ord = next(self.ord_gen)
        self.is_main = is_main
        self.choice = choice

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return instance.__fields__[self.name]
        except KeyError:
            if self.default is UNDEF:
                raise AttributeError(self.name)
            if callable(self.default):
                val = self.default()
            else:
                val = self.default
            instance.__fields__[self.name] = val
            return val

    def __set__(self, instance, value):
        instance.__fields__[self.name] = value

    def __delete__(self, instance):
        del instance.__fields__[self.name]

    def __set_name__(self, owner, name):
        self.name = name


class LazyYamlField(YamlField):
    "A YamlField that is rendered the first time it's accessed"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return instance.__fields__[self.name]
        except KeyError:
            if self.name in instance.__lazy_fields__:
                return self._render_lazy(instance)
            if self.default is UNDEF:
                raise AttributeError(self.name)
            if callable(self.default):
                val = self.default()
            else:
                val = self.default
            instance.__fields__[self.name] = val
            return val

    def _render_lazy(self, instance):
        raise NotImplementedError()


class DictField:
    """Marker class for fields that require a yaml mapping"""
    pass


class ArrayField:
    """Marker class for fields that require a yaml array"""
    pass


class ScalarField:
    """Marker class for fields that require a yaml scalar"""
    pass


class ObjField(YamlField, DictField):
    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        instance.__fields__[self.name] = self.klass(**value)


class LazyObjField(LazyYamlField, DictField):
    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        try:
            del instance.__fields__[self.name]
        except KeyError:
            pass
        instance.__lazy_fields__[self.name] = value

    def _render_lazy(self, instance):
        data = instance.__ctx__.render(instance.__lazy_fields__[self.name])
        return self.klass(**data)


class BooleanField(YamlField, ScalarField):
    pass


class StringField(YamlField, ScalarField):
    pass


class IntField(YamlField, ScalarField):
    pass


class MappingField(YamlField, DictField):
    pass


class ListField(YamlField, ArrayField):
    def __init__(self, item_type=None, **kwargs):
        super().__init__(**kwargs)
        self.item_type = item_type

    def __set__(self, instance, value):
        if not isinstance(value, list):
            raise ValueError(
                "{} expects a yaml list, got {}".format(
                    type(self), type(value)))
        instance.__fields__[self.name] = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        val = super().__get__(instance, owner)
        if self.item_type is None:
            return val
        return [self.item_type(i) for i in val]


class YamlLoaderVisitor:
    def extract_fields(self, loader):
        if isinstance(loader, YamlLoader):
            cls = type(loader)
        elif issubclass(loader,YamlLoader):
            cls = loader
        else:
            raise ValueError("loader must be a YamlLoader subclass or instance")
        fields = [
                (name, field, getattr(loader, name))
                for (name, field) in cls.__dict__.items()
                if isinstance(field, YamlField)]
        fields.sort(key=lambda x: x[1].ord)
        return fields

    def visit(self, loader):
        fields = self.extract_fields(loader)
        return [(name, self.visit_field(field, val)) for (name, field, val) in fields]

    def visit_field(self, field, val):
        cls = type(field)
        # get the first visitable class in field's __mro__
        for parent in cls.__mro__:
            name = "visit_%s" % parent.__name__.lower()
            if hasattr(self, name):
                return getattr(self, name)(field, val)
        raise ValueError(field)

    def visit_objfield(self, field, val):
        return self.__class__().visit(val)

    def visit_lazyobjfield(self, field, val):
        return self.__class__().visit(val)

    def visit_stringfield(self, field, val):
        return self.visit_generic(field, val)

    def visit_mappingfield(self, field, val):
        return self.visit_generic(field, val)

    def visit_listfield(self, field, val):
        return self.visit_generic(field, val)

    def visit_booleanfield(self, field, val):
        return self.visit_generic(field, val)

    def visit_generic(self, field, val):
        raise NotImplementedError()


class YamlLoaderScaffolder(YamlLoaderVisitor):
    def __init__(self, indent=0, comments=False):
        self.data = CommentedMap()
        self._indent = indent
        self.comments = comments

    def dumps(self):
        output = StringIO()
        self.dump(output)
        return output.getvalue()

    def dump(self, output):
        yaml = YAML()
        return yaml.dump(self.data, output)

    def add_comment(self, key, comment):
        if not self.comments:
            return
        self.data.yaml_set_comment_before_after_key(key, comment,
                                                    indent=self._indent)

    def visit(self, loader):
        fields = CommentedMap()
        self.data[loader.__yaml_name__] = fields
        if loader.__doc__:
            doc = loader.__doc__.strip().splitlines()[0]
        else:
            doc = None
        self.add_comment(loader.__yaml_name__, doc)
        self._indent += 2
        loader_data = self.data
        self.data = fields
        self.visit_yaml_obj(loader, loader)
        self.data = loader_data

    def visit_yaml_obj(self, loader, value):
        for (name, field, val) in self.extract_fields(loader):
            self.data[name] = self.visit_field(field, val)
            self.add_comment(name, field.help)
        self._indent -= 2

    def visit_field(self, field, val):
        data = self.data
        super().visit_field(field, val)
        field_data = self.data
        if field_data is UNDEF:
            field_data = "UNDEFINED!"
        self.data = data
        return field_data

    def visit_stringfield(self, field, val):
        self.data = field.default

    def visit_generic(self, field, val):
        self.data = []

    def visit_booleanfield(self, field, val):
        self.data = field.default and "yes" or "no"

    def visit_lazyobjfield(self, field, val):
        data = self.data
        self.data = CommentedMap()
        self._indent += 2
        self.visit_yaml_obj(field.klass, val)

    def visit_yamlloader(self, field, val):
        val.__yaml_name__ = field.name
        sub_dumper = self.__class__(
            indent=self._indent+1,
            comments=self.comments).visit(val)
        return sub_dumper.data


class YamlLoaderRenderer(YamlLoaderVisitor):
    def __init__(self, indent=0, output=None, comments=False):
        self.output = StringIO() if output is None else output
        self._indent = indent
        self.comments = comments

    def indent(self):
        self.output.write("  " * self._indent)

    def writeln(self, txt):
        self.indent()
        self.output.write(txt)
        self.output.write("\n")

    def write_comment(self, field):
        if not self.comments:
            return
        if field.help:
            self.writeln("# %s" % field.help)
        if field.default is not UNDEF:
            self.writeln("# Default: %s" % field.default)

    def visit(self, loader):
        for (name, field, val) in self.extract_fields(loader):
            self.write_comment(field)
            self.indent()
            self.output.write("%s: " % name)
            self.visit_field(field, val)

    def visit_scalar(self, val):
        if isinstance(val, dict):
            return self.visit_dict(val)
        if isinstance(val, list):
            return self.visit_list(val)
        if isinstance(val, str):
            return self.visit_str(val)
        if isinstance(val, bool):
            return self.visit_bool(val)
        if isinstance(val, int):
            return self.visit_int(val)
        if isinstance(val, float):
            return self.visit_float(val)
        if val is None:
            return self.visit_none(val)
        raise ValueError("%s is not a yamltype")

    def visit_str(self, val):
        # TODO: handle multi-line txt
        self.output.write(repr(val))
        self.output.write("\n")

    def visit_int(self, val):
        self.output.write(repr(val))
        self.output.write("\n")

    def visit_none(self, val):
        self.output.write("null\n")

    def visit_bool(self, val):
        val = "yes" if val else "no"
        self.output.write(val)
        self.output.write("\n")

    def visit_objfield(self, field, val):
        self.output.write("\n")
        self.visit_yamlloader(val)

    def visit_lazyobjfield(self, field, val):
        self.output.write("\n")
        self.visit_yamlloader(val)

    def visit_yamlloader(self, val):
        self.__class__(
            indent=self._indent+1,
            comments=self.comments,
            output=self.output).visit(val)

    def visit_generic(self, field, val):
        self.visit_scalar(val)

    def visit_mappingfield(self, field, val):
        if not val:
            self.output.write("{}\n")
            return
        self.output.write("\n")
        self._indent += 1
        for k, v in val.items():
            self.indent()
            self.output.write("%s: " % k)
            self.visit_scalar(v)
        self._indent -= 1

    def visit_listfield(self, field, val):
        if not val:
            self.output.write("[]\n")
            return
        self.output.write("\n")
        self._indent += 1
        for item in val:
            if isinstance(item, YamlLoader):
                self.writeln("- %s:" % item.__yaml_name__)
                self._indent += 1
                self.visit_yamlloader(item)
                self._indent -= 1
            else:
                self.writeln("- %s" % str(item))
        self._indent -= 1


def yamlloader_as_yaml(loader, comments=False, indent=0, name=None,
                       output=None):
    output = StringIO() if output is None else output
    if name is not None:
        output.write(name + ":\n")
        indent += 1
    renderer = YamlLoaderRenderer(indent=indent,
                                  comments=comments, output=output)
    renderer.visit(loader)
    if hasattr(renderer.output, "getvalue"):
        return renderer.output.getvalue()


class YamlVisitor:
    def visit(self,  data):
        if isinstance(data, dict):
            return self.visit_dict(data)
        if isinstance(data, list):
            return self.visit_list(data)
        if isinstance(data, str):
            return self.visit_str(data)
        if isinstance(data, int):
            return self.visit_int(data)
        if isinstance(data, float):
            return self.visit_float(data)
        if data is None:
            return self.visit_none(data)
        return self.visit_generic(data)

    def visit_dict(self, data):
        return {k: self.visit(v) for (k, v) in data.items()}

    def visit_list(self, data):
        return [self.visit(i) for i in data]

    def visit_str(self, data):
        return data

    def visit_int(self, data):
        return data

    def visit_float(self, data):
        return data

    def visit_none(self, data):
        return data

    def visit_generic(self, data):
        raise NotImplementedError(type(data))
