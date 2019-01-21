import yaml
import jinja2
import warnings

from collections.abc import MutableMapping


NOTFOUND = object()


class UndefinedError(Exception):
    def __init__(self, help):
        self.help = help
        self.path = []
        self.template = None

    def __str__(self):
        return ("`{}` is not defined.\nhelp: {}\n" +
                "template was: `{}`").format(
            ".".join(reversed(self.path)),
            self.help,
            self.template)


class ContextBase:

    @classmethod
    def from_data(cls, data, root):
        if isinstance(data, ContextBase):
            data = data._raw()
        if isinstance(data, dict):
            return MappingContext(data, root)
        elif isinstance(data, list):
            return ArrayContext(data, root)
        elif isinstance(data, str):
            return StringContext(data, root)
        else:
            return ScalarContext(data, root)

    def _render(self):
        raise NotImplementedError()

    def _raw(self):
        raise NotImplementedError()

    def _copy(self):
        return self.__class__.from_data(self._raw(), self.root)


class ScalarContext(ContextBase):
    def __init__(self, data, root):
        self.root = root
        self.data = data

    def _render(self):
        return self.data

    def _raw(self):
        return self.data


class StringContext(ScalarContext):
    def _render(self):
        return self.root._render_string_ctx(self)

    def __str__(self):
        return self._render()


class ArrayContext(ContextBase):
    def __init__(self, data, root):
        self.root = root
        self.data = [self.from_data(item, root) for item in data]

    def _render(self):
        return [i._render() for i in self.data]

    def _raw(self):
        return [r._raw() for r in self.data]

    def append(self, data):
        self.data.append(self.from_data(data, self.root))

    def __contains__(self, data):
        if isinstance(data, ContextBase):
            data = data._raw()
        return data in self._raw()

    def __iter__(self):
        return self.data.__iter__()


class MappingContext(ContextBase, MutableMapping):
    def __init__(self, data, root):
        self.root = root
        self.data = {k: self.from_data(v, root) for k, v in data.items()}
        self._env = None

    def __setitem__(self, key, value):
        self.data[key] = self.from_data(value, self.root)

    def __getitem__(self,  key):
        data = self.data[key]
        if isinstance(data, ScalarContext):
            return data._render()
        return data

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return len(self.data)

    def get_path(self, path, default=NOTFOUND):
        try:
            try:
                key, rest = path.split(".", 1)
            except ValueError:
                return self[path]
            else:
                return self.data[key].get_path(rest)
        except KeyError:
            if default is not NOTFOUND:
                return default
            else:
                raise

    def bind(self, path, value, create=False):
        try:
            key, rest = path.split(".", 1)
        except ValueError:
            self[path] = value
        else:
            try:
                self.data[key].bind(rest, value, create=create)
            except KeyError:
                if create:
                    self[key] = {}
                    self.data[key].bind(rest, value, create=create)
                else:
                    raise

    def update(self, other):
        for k, v in other.items():
            if isinstance(v, (MappingContext, dict)) and isinstance(self.data.get(k), (MappingContext, dict)):
                self.data[k].update(v)
            else:
                self[k] = v

    def keys(self):
        if "$<" in self.data:
            extended = self.root.get_path(self["$<"])
            return {
                    self.root.render(k) for k in self if k != "$<"
                } | {self.root.render(k) for k in extended.keys()}
        return {k for k in self}

    def _render(self):
        if "$<" in self.data:
            epath = self["$<"]
            extended = self.root.get_path(epath)
            if isinstance(extended, ArrayContext):
                return extended._copy()._render()
            if not isinstance(extended, MappingContext):
                raise ValueError("Can't extend `%s`, it's not a map." % epath)
            result = extended._render()
            overlay = {
                    self.root.render(k): self.root.render(v)
                    for (k, v)
                    in self.data.items() if k != "$<"}
            return mergedicts(result, overlay)
        else:
            return {self.root.render(k): self.root.render(v)
                    for (k, v) in self.data.items()}

    def _raw(self):
        return {k: v._raw() for (k, v) in self.data.items()}


def mergedicts(dest, src):
    "merges b into a"
    for key in src:
        if (key in dest
                and isinstance(dest[key], dict)
                and isinstance(src[key], dict)):
            mergedicts(dest[key], src[key])
        else:
            dest[key] = src[key]
    return dest


class Context(MappingContext):
    def __init__(self, src=None, data=None):
        self._env = None
        if src is not None:
            data = yaml.load(src)
        else:
            data = data if data else {}
        super().__init__(data, self)

    @property
    def env(self):
        if self._env is None:
            self._env = jinja2.Environment()
            # self._env.globals['undefined'] = self.undefined
            for cls in RenderFunctionsRegistry.funcs:
                self._env.globals[cls.func_name] = cls(self)
        return self._env

    def _render_string_ctx(self, ctx):
        try:
            return self.env.from_string(ctx.data).render((k, v) for (k, v) in self.data.items() if v is not ctx)
        except UndefinedError as e:
            e.template = ctx.data
            raise
        except Exception:
            return ctx.data

    def render_dict(self, template):
        if "$<" in template:
            epath = template["$<"]
            extended = self.get_path(epath)
            if not isinstance(extended, MappingContext):
                raise ValueError("Can't extend `%s`, it's not a map." % epath)
            result = extended._render()
            overlay = {
                    self.render(k): self.render(v)
                    for (k, v)
                    in template.items() if k != "$<"}
            return mergedicts(result, overlay)
        else:
            return {self.render(k): self.render(v)
                    for (k, v) in template.items()}

    def render(self, template):
        if isinstance(template, str) and "{" in template:
            try:
                return self.env.from_string(template).render(self)
            except UndefinedError as e:
                e.template = template
                raise
            except Exception as e:
                warnings.warn("Error while rendering `%s`: \n%s" % (template, str(e)))
                return template
        elif isinstance(template, dict):
            return self.render_dict(template)
            # return {self.render(k): self.render(v) for (k, v) in template.items()}
        elif isinstance(template, list):
            return [self.render(i) for i in template]
        elif isinstance(template, ContextBase):
            return template._render()
        else:
            return template

    def undefined(self, help=None):
        raise UndefinedError(help)

    def copy(self):
        return self.__class__(data=self._raw())


def context_from_file(file):
    return Context(file)


class RenderFunctionsRegistry(type):
    funcs = set()

    def __init__(cls, name, bases, attrs):
        if name != "RenderFunction":
            RenderFunctionsRegistry.funcs.add(cls)


class RenderFunction(metaclass=RenderFunctionsRegistry):
    def __init__(self, ctx):
        self.ctx = ctx

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


class Undefined(RenderFunction):
    func_name = "undefined"

    def __call__(self, help=None):
        raise UndefinedError(help)
