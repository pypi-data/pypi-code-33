from typing import List, TypeVar, Generic, Type, Dict, Callable, Optional

R = TypeVar('R')
A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class Bound:

    def __init__(self, cls: str) -> None:
        self.cls = cls

    def __repr__(self) -> str:
        return f'Bound({self.cls})'


class Kind:
    pass


class Nullary(Kind):

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name


class Wildcard(Kind):

    def __repr__(self) -> str:
        return '_'


class HK(Kind):

    def __init__(self, name: str, params: List[Kind]) -> None:
        self.name = name
        self.params = params

    def __repr__(self) -> str:
        params = ', '.join(map(str, self.params))
        return f'{self.name}[{params}]'


class Par:
    pass


class Mono(Par):

    def __init__(self, tpe: type) -> None:
        self.tpe = tpe

    def __repr__(self) -> str:
        return self.tpe


class Poly(Par):

    def __init__(self, kind: Kind, bounds: List[Bound]=[]) -> None:
        self.kind = kind
        self.bounds = bounds

    def __repr__(self) -> str:
        bounds = ''.join((f' <: {b}' for b in self.bounds))
        return f'{self.kind}{bounds}'


class Signature:

    def __init__(self, input: List[Par], output: Par) -> None:
        self.input = input
        self.output = output

    def __repr__(self) -> str:
        input = ', '.join(map(str, self.input))
        return f'({input}) => {self.output}'


class ClassFunction:
    pass


class ClassFunction1(Generic[R, A], ClassFunction):

    def __init__(self, name: str, signature: Signature, par: Type[A], ret: Type[R]) -> None:
        self.name = name
        self.signature = signature
        self.par = par
        self.ret = ret


class ClassFunction2(Generic[R, A, B], ClassFunction):

    def __init__(self, name: str, signature: Signature, par1: Type[A], par2: Type[B], ret: Type[R]) -> None:
        self.name = name
        self.signature = signature
        self.par1 = par1
        self.par2 = par2
        self.ret = ret
        self.cls: Optional[str] = None

    def set_class(self, cls: 'Class') -> None:
        self.cls = cls.name
        self.resolver = cons_resolver(cls, self.signature)

    def __call__(self, a: A) -> Callable[[B], R]:
        inst = find_instance(self.cls, type(a))


class Class:

    @staticmethod
    def cons(name: str, params: List[Par], functions: List[ClassFunction]) -> 'Class':
        cls = Class(name, params, [f for f in functions])
        for f in functions:
            f.set_class(cls)
        return cls


    def __init__(self, name: str, params: List[Par], functions: List[ClassFunction]) -> None:
        self.name = name
        self.params = params
        self.functions = functions


class Instance(Generic[A]):

    def __init__(self, cls: Class, tpe: Type[A], functions: Dict[str, ClassFunction]) -> None:
        self.cls = cls
        self.tpe = tpe
        self.functions = functions


class Instances:

    def __init__(self) -> None:
        self.registry: Dict[str, Dict[type, Instance]] = dict()


instances = Instances()


def register(cls: str, inst: Instance[A]) -> None:
    instances.registry.setdefault(cls, dict())
    print(inst.tpe)
    instances.registry[cls][inst.tpe] = inst


def instance(cls: Class, tpe: A, **functions: ClassFunction) -> None:
    inst = Instance(cls, tpe, functions)
    register(cls.name, inst)


def find_instance(name: str, tpe: Type[A]) -> None:
    return instances.registry[name][tpe]


class HK1(Generic[A]):
    pass


def cons_resolver(cls: Class, signature: Signature) -> Callable:
    print(cls.params)
    print(signature)
    def resolver(a) -> None:
        return
    return resolver


__all__ = ('Bound', 'Kind', 'Nullary', 'HK', 'Par', 'Mono', 'Poly', 'Signature', 'ClassFunction', 'Class', 'Instance',
           'Wildcard',)
