# system modules
import importlib
import re

# internal modules
import polt

# external modules
import click


def option_spec(ctx, param, value):
    part = iter(value.split("=", maxsplit=1))
    attr, value = next(part, ""), next(part, True)
    if attr:
        return re.sub(r"\s+", "-", attr), value
    else:
        raise click.BadParameter(
            _(
                "specify an option like {option}={value}, not like {given}"
            ).format(
                option=_("option").upper(),
                value=_("value").upper(),
                given=repr(value),
            ),
            param=param,
            ctx=ctx,
        )


def options_spec(ctx, param, value):
    return dict(map(lambda x: option_spec(ctx, param, x), value))


def python_class_spec(aliases={}):
    def spec(ctx, param, value):
        if value is None:
            return value
        matching_alias_cls = next(
            (cls for al, cls in aliases.items() if value in al), None
        )
        if matching_alias_cls:
            cls = matching_alias_cls
        else:
            parts = value.split(".")
            try:
                package, classname = ".".join(parts[:-1]), parts[-1]
                if package:
                    module = importlib.import_module(package)
                    cls = getattr(module, classname)
                    assert isinstance(cls, type), _(
                        "{obj} is not a type but of type {type}"
                    ).format(obj=cls, type=type(cls))
                else:
                    cls = aliases[classname]
            except (
                IndexError,
                ImportError,
                AttributeError,
                AssertionError,
                ValueError,
                KeyError,
            ) as e:
                raise click.BadParameter(
                    _(
                        "class path specification {spec} "
                        "is neither a native alias (like {native_aliases}) "
                        "nor an importable class specification ({error})"
                        ""
                    ).format(
                        spec=repr(value),
                        native_aliases=polt.l10n.join(
                            polt.extensions.EntryPointExtensions.short_aliases(
                                aliases
                            ),
                            last_sep=" {} ".format(_("or")),
                        ),
                        error=e,
                    ),
                    ctx=ctx,
                    param=param,
                )
        path = ".".join((cls.__module__, cls.__name__))
        return path

    return spec
