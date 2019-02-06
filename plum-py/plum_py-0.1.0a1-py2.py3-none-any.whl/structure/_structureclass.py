# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from .._plumclass import PlumClass
from ._member import Member


class StructureClass(PlumClass):

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        nbytes = 0

        members = dict()
        for name, member_cls in getattr(cls, '__annotations__', {}).items():
            try:
                nbytes += member_cls._nbytes
            except TypeError:
                # must be None
                nbytes = None
            except AttributeError:
                raise TypeError(f'Structure member {name!r} must be a Plum subclass (or Varies)')

            try:
                member = getattr(cls, name)
            except AttributeError:
                member = Member()
                setattr(cls, name, member)
            else:
                if not isinstance(member, Member):
                    member = Member(default=member)
                    setattr(cls, name, member)

            member._cls = member_cls
            member.name = name
            members[name] = member

        cls._members = members
        cls._nbytes = nbytes

    def __call__(cls, *args, **kwargs):
        if args or not kwargs:
            if len(args) > 1:
                excess_args = (
                    f'{cls.__qualname__} expected at most 1 positional arguments, '
                    f'got {len(args)}')
                raise TypeError(excess_args)
            elif args:
                mapping = args[0]
                if not isinstance(mapping, dict):
                    # support iterable of (name, value) pairs
                    mapping = dict(mapping)
                elif kwargs:
                    mapping = mapping.copy()
                mapping.update(kwargs)
            else:
                mapping = dict()
        else:
            mapping = kwargs

        members = cls._members

        extras = set(mapping) - set(members)

        if extras:
            s = 's' if len(extras) > 1 else ''
            invalid_members = (
                f'{cls.__qualname__}() '
                f'got {len(extras)} unexpected members{s} ')
            invalid_members += ', '.join(repr(m) for m in members if m in extras)
            raise TypeError(invalid_members)

        values = [mapping.get(n, m.default) for n, m in members.items()]

        missing = [n for n, v in zip(members, values) if v is None]

        if missing:
            s = 's' if len(missing) > 1 else ''
            missing_members = (
                f'{cls.__qualname__}() '
                f'missing {len(missing)} required keyword-only argument{s} ')
            missing_members += ', '.join(missing)
            raise TypeError(missing_members)

        self = dict.__new__(cls)
        dict.__init__(self)

        for member, value in zip(members.values(), values):
            mbr_cls = member.get_cls(self)
            if type(value) is mbr_cls:
                dict.__setitem__(self, member.name, value)
            else:
                dict.__setitem__(self, member.name, mbr_cls(value))

        return self
