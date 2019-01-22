import base64
import collections
import copy
import importlib
import inspect
import numbers
import pickle
import re
import types
import typing

import frozendict  # type: ignore
import numpy  # type: ignore
import typing_inspect  # type: ignore
from pytypes import type_util  # type: ignore
from scipy import special as scipy_special  # type: ignore
from sklearn.utils import validation as sklearn_validation  # type: ignore

from . import base
from d3m import exceptions, utils

__all__ = (
    'Hyperparameter', 'Primitive', 'Constant', 'Bounded', 'Enumeration', 'UniformBool', 'UniformInt',
    'Uniform', 'LogUniform', 'Normal', 'LogNormal', 'Union', 'Choice', 'Set', 'Hyperparams',
)

RandomState = typing.Union[numbers.Integral, numpy.integer, numpy.random.RandomState]

T = typing.TypeVar('T')

# We want to make sure we do not support dots because they are used to delimit nested hyper-parameters.
HYPERPARAMETER_NAME_REGEX = re.compile(r'^[A-Za-z][A-Za-z_0-9]*$')


def _get_structural_type_argument(obj: typing.Any) -> type:
    cls = typing_inspect.get_generic_type(obj)

    return utils.get_type_arguments(cls)[T]


def check_sample_size(obj: 'typing.Union[Hyperparameter, Hyperparams]', min_samples: int, max_samples: typing.Optional[int]) -> typing.Tuple[int, int]:
    all_max_samples = obj.get_max_samples()

    if not isinstance(min_samples, int):
        raise exceptions.InvalidArgumentTypeError("'min_samples' argument is not an int.")
    if min_samples < 0:
        raise exceptions.InvalidArgumentValueError("'min_samples' cannot be smaller than 0.")
    if max_samples is not None:
        if not isinstance(max_samples, int):
            raise exceptions.InvalidArgumentTypeError("'max_samples' argument is not an int.")
        if min_samples > max_samples:
            raise exceptions.InvalidArgumentValueError("'min_samples' cannot be larger than 'max_samples'.")
        if all_max_samples is not None and max_samples > all_max_samples:
            raise exceptions.InvalidArgumentValueError("'max_samples' cannot be larger than {max_samples}.".format(max_samples=all_max_samples))
    else:
        if all_max_samples is not None:
            max_samples = all_max_samples
        else:
            raise exceptions.InvalidArgumentTypeError("'max_samples' argument is required.")

    return min_samples, max_samples


# A special Python method which is stored efficiently
# when pickled. See PEP 307 for more details.
def __newobj__(cls: type, *args: typing.Any) -> typing.Any:
    return cls.__new__(cls, *args)


def _is_defined_at_global_scope(cls: type) -> bool:
    class_name = getattr(cls, '__name__', None)
    class_module = inspect.getmodule(cls)
    return class_name is not None and class_module is not None and getattr(class_module, class_name, None) is cls


def _recreate_hyperparams_class(base_cls: 'typing.Type[Hyperparams]', define_args_list: typing.Sequence[typing.Dict[str, typing.Any]]) -> typing.Any:
    # We first have to recreate the class from the base class.
    cls = base_cls
    for args in define_args_list:
        cls = cls.define(**args)
    # And then we create a new instance of the object.
    return cls.__new__(cls)


def _encode_generic_type(structural_type: type) -> typing.Union[type, typing.Dict]:
    args = typing_inspect.get_last_args(structural_type)

    if not args:
        return structural_type

    return {
        'origin': typing_inspect.get_origin(structural_type),
        'args': [_encode_generic_type(arg) for arg in args]
    }


def _decode_generic_type(description: typing.Union[type, typing.Dict]) -> type:
    if not isinstance(description, dict):
        return description

    return description['origin'][tuple(_decode_generic_type(arg) for arg in description['args'])]


class HyperparameterMeta(utils.AbstractMetaclass, typing.GenericMeta):
    pass


class Hyperparameter(typing.Generic[T], metaclass=HyperparameterMeta):
    """
    A base class for hyper-parameter descriptions.

    A base hyper-parameter does not give any information about the space of the hyper-parameter,
    besides a default value.

    Type variable ``T`` is optional and if not provided an attempt to automatically infer
    it from ``default`` will be made. Attribute ``structural_type`` exposes this type.

    There is a special case when values are primitives. In this case type variable ``T`` and
    ``structural_type`` should always be a primitive base class, but valid values used in
    hyper-parameters can be both primitive instances (of that base class or its subclasses)
    and primitive classes (that base class itself or its subclasses). Primitive instances
    allow one to specify a primitive much more precisely: values of their hyper-parameters,
    or even an already fitted primitive.

    This means that TA2 should take care and check if values it is planning to use for
    this hyper-parameter are a primitive class or a primitive instance. It should make sure
    that it always passes only a primitive instance to the primitive which has a hyper-parameter
    expecting primitive(s). Even if the value is already a primitive instance, it must not
    pass it directly, but should make a copy of the primitive instance with same hyper-parameters
    and params. Primitive instances part of hyper-parameter definitions should be seen
    as immutable and as a template for primitives to pass and not to directly use.

    TA2 is in the best position to create such instances during pipeline run as it has all
    necessary information to construct primitive instances (and can control a random seed,
    or example). Moreover, it is also more reasonable for TA2 to handle the life-cycle of
    a primitive and do any additional processing of primitives. TA2 can create such a primitive
    outside of the pipeline, or as part of the pipeline and pass it as a hyper-parameter
    value to the primitive. The latter approach allows pipeline to describe how is the primitive
    fitted and use data from the pipeline itself for fitting, before the primitive is passed on
    as a hyper-parameter value to another primitive.

    Attributes
    ----------
    name : str
        A name of this hyper-parameter in the configuration of all hyper-parameters.
    structural_type : type
        A Python type of this hyper-parameter. All values of the hyper-parameter, including the default value,
        should be of this type.
    semantic_types : Sequence[str]
        A list of URIs providing semantic meaning of the hyper-parameter. This can help express how
        the hyper-parameter is being used, e.g., as a learning rate or as kernel parameter.
    description : str
        An optional natural language description of the hyper-parameter.
    """

    def __init__(self, default: T, *, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        if semantic_types is None:
            semantic_types = ()

        self.name: str = None
        self.semantic_types = semantic_types
        self.description = description

        self._default = default

        # If subclass has not already set it.
        if not hasattr(self, 'structural_type'):
            structural_type = _get_structural_type_argument(self)

            if structural_type == typing.Any:
                structural_type = self.infer_type(self._default)

            self.structural_type = structural_type

        self.validate_default()

    def contribute_to_class(self, name: str) -> None:
        if self.name is not None and self.name != name:
            raise exceptions.InvalidStateError("Name is already set to '{name}', cannot set to '{new_name}'.".format(name=self.name, new_name=name))

        self.name = name

    def get_default(self, path: str = None) -> typing.Any:
        """
        Returns a default value of a hyper-parameter.

        Remember to never modify it in-place it is a mutable value. Moreover, if it is
        an instance of a primitive, also copy the instance before you use it to not
        change its internal state.

        Parameters
        ----------
        path : str
            An optional path to get defaults for nested hyper-parameters, if a hyper-parameter
            has nested hyper-parameters. It can contain ``.`` to represent a path through
            nested hyper-parameters.

        Returns
        -------
        Any
            A default value.
        """

        if path is not None:
            raise KeyError("Invalid path '{path}'.".format(path=path))

        return self._default

    def check_type(self, value: typing.Any, cls: type) -> bool:
        """
        Check that the type of ``value`` matches given ``cls``.

        There is a special case if ``value`` is a primitive class, in that case it is checked
        that ``value`` is a subclass of ``cls``.

        Parameters
        ----------
        value : Any
            Value to check type for.
        cls : type
            Type to check type against.

        Returns
        -------
        bool
            ``True`` if ``value`` is an instance of ``cls``, or if ``value`` is a primitive
            class, if it is a subclass of ``cls``.
        """

        # Importing here to prevent import cycle.
        from d3m.primitive_interfaces import base as primitive_interfaces_base

        def get_type(obj: typing.Any) -> type:
            if utils.is_type(obj) and issubclass(obj, primitive_interfaces_base.PrimitiveBase):
                return obj
            else:
                return type(obj)

        value_type = type_util.deep_type(value, get_type=get_type)

        return utils.is_subclass(value_type, cls)

    def infer_type(self, value: typing.Any) -> type:
        """
        Infers a structural type of ``value``.

        There is a special case if ``value`` is a primitive class, in that case it is returned
        as is.

        Parameters
        ----------
        value : Any
            Value to infer a type for.

        Returns
        -------
        type
            Type of ``value``, or ``value`` itself if ``value`` is a primitive class.
        """

        # Importing here to prevent import cycle.
        from d3m.primitive_interfaces import base as primitive_interfaces_base

        if utils.is_type(value) and issubclass(value, primitive_interfaces_base.PrimitiveBase):
            return value
        else:
            return utils.get_type(value)

    def validate(self, value: T) -> None:
        """
        Validates that a given ``value`` belongs to the space of the hyper-parameter.

        If not, it throws an exception.

        Parameters
        ----------
        value : Any
            Value to validate.
        """

        if not self.check_type(value, self.structural_type):
            raise exceptions.InvalidArgumentTypeError("Value '{value}' {for_name}is not an instance of the structural type: {structural_type}".format(
                value=value, for_name=self._for_name(), structural_type=self.structural_type,
            ))

    def validate_default(self) -> None:
        """
        Validates that a default value belongs to the space of the hyper-parameter.

        If not, it throws an exception.
        """

        self.validate(self._default)

    def _for_name(self) -> str:
        if self.name is None:
            return ""
        else:
            return "for hyper-parameter '{name}' ".format(name=self.name)

    def sample(self, random_state: RandomState = None) -> T:
        """
        Samples a random value from the hyper-parameter search space.

        For the base class it always returns a ``default`` value because the space
        is unknown.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        sklearn_validation.check_random_state(random_state)

        return self.get_default()

    def get_max_samples(self) -> typing.Optional[int]:
        """
        Returns a maximum number of samples that can be returned at once using `sample_multiple`.

        Returns
        -------
        int
            A maximum number of samples that can be returned at once. Or ``None`` if there is no limit.
        """

        return 1

    def _check_sample_size(self, min_samples: int, max_samples: typing.Optional[int]) -> typing.Tuple[int, int]:
        return check_sample_size(self, min_samples, max_samples)

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        For the base class it always returns only a ``default`` value because the space
        is unknown.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        if min_samples > 0:
            assert min_samples == 1, min_samples
            assert max_samples == 1, max_samples
            return (self.get_default(),)
        elif max_samples < 1:
            assert min_samples == 0, min_samples
            assert max_samples == 0, max_samples
            return ()
        else:
            assert min_samples == 0, min_samples
            assert max_samples == 1, max_samples
            return typing.cast(typing.Sequence[T], () if random_state.rand() >= 0.5 else (self.get_default(),))

    def __repr__(self) -> str:
        return '{class_name}(default={default})'.format(
            class_name=type(self).__name__,
            default=self.get_default(),
        )

    def to_simple_structure(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a simple structure, similar to JSON, but with values
        left as Python values.

        Returns
        -------
        Dict
            A dict.
        """

        structure = {
            'type': type(self),
            'default': self.get_default(),
            'structural_type': self.structural_type,
            'semantic_types': list(self.semantic_types),
        }

        if self.description is not None:
            structure['description'] = self.description

        return structure

    # TODO: Rename to "value_to_json_structure".
    def value_to_json(self, value: T) -> typing.Any:
        """
        Converts a value of this hyper-parameter to a JSON-compatible value.

        Parameters
        ----------
        value : Any
            Value to convert.

        Returns
        -------
        Any
            A JSON-compatible value.
        """

        self.validate(value)

        if utils.is_subclass(self.structural_type, typing.Union[str, int, float, bool, type(None)]):
            return value
        else:
            return base64.b64encode(pickle.dumps(value)).decode('utf8')

    # TODO: Rename to "value_from_json_structure".
    def value_from_json(self, json: typing.Any) -> T:
        """
        Converts a JSON-compatible value to a value of this hyper-parameter.

        Parameters
        ----------
        json : Any
            A JSON-compatible value.

        Returns
        -------
        Any
            Converted value.
        """

        if utils.is_subclass(self.structural_type, typing.Union[str, int, float, bool, type(None)]):
            value = json
        else:
            # TODO: Limit the types of values being able to load to prevent arbitrary code execution by a malicious pickle.
            value = pickle.loads(base64.b64decode(json.encode('utf8')))

        self.validate(value)

        return value

    def traverse(self) -> 'typing.Iterator[Hyperparameter]':
        """
        Traverse over all child hyper-parameters of this hyper-parameter.

        Yields
        ------
        Hyperparamater
            The next child hyper-parameter of this hyper-parameter.
        """

        # Empty generator by default.
        yield from ()  # type: ignore

    def transform_value(self, value: T, transform: typing.Callable, index: int = 0) -> T:
        """
        Transforms the value belonging to this hyper-parameter to a new value by
        calling ``transform`` on it. If the hyper-parameter has child
        hyper-parameters, it deconstructs the value, calls ``transform_value``
        recursively, and constructs the new value back.

        Parameters
        ----------
        value : Any
            A value to transform.
        transform : Callable
            A function which receives as arguments: a hyper-parameter instance,
            the value, and a sequence index of iterating over a structure, and
            should return a new transformed value. It is called only for leaf
            hyper-parameters (those without child hyper-parameters).
        index : int
            A sequence index which should be passed to ``transform``.
            Used when iterating over a structure by the parent.
            It should be deterministic.

        Returns
        -------
        Any
            A transformed value.
        """

        return transform(self, value, index)

    def can_accept_value_type(self, structural_type: typing.Union[type, typing.List[type]]) -> bool:
        """
        Returns ``True`` if a hyper-parameter can accept a value of type ``structural_type``.

        Parameters
        ----------
        structural_type : Union[type, List[type]]
            A structural type. Can be a type or a list of types.

        Returns
        -------
        bool
            If value of given type can be accepted by this hyper-parameter.
        """

        if structural_type is typing.Any:
            return True
        elif isinstance(structural_type, typing.List):
            # Default implementation does not support a list of types. This is used for "Set" hyper-parameter.
            return False
        else:
            return utils.is_subclass(structural_type, self.structural_type)

    # TODO: Remove once using Python 3.7 exclusively.
    def __getstate__(self) -> dict:
        state = dict(self.__dict__)
        # Subclasses of generic classes cannot be pickled in Python 3.6, but instances of
        # them can, because during runtime information about generic classes is removed.
        # Pickling of hyper-parameter instances thus generally work without problems
        # but if they are an instance of the a subclass of a generic class, a reference
        # to that class is stored into "__orig_class__" which cannot be pickled.
        # Because we do not really need it after we extracted "structural_type",
        # we remove it here when pickling.
        # See: https://gitlab.com/datadrivendiscovery/d3m/issues/155
        if '__orig_class__' in state:
            del state['__orig_class__']

        if 'structural_type' in state:
            # A workaround for structural type being a generic class.
            state['structural_type'] = _encode_generic_type(state['structural_type'])

        return state

    def __setstate__(self, state: dict) -> None:
        if 'structural_type' in state:
            state['structural_type'] = _decode_generic_type(state['structural_type'])

        self.__dict__ = state


class Primitive(Hyperparameter[T]):
    """
    A hyper-parameter describing a primitive or primitives.

    Matching primitives are determined based on their structural type (a matching primitive
    has to be an instance or a subclass of the structural type), their primitive's family
    (a matching primitive's family has to be among those listed in the hyper-parameter),
    their algorithm types (a matching primitive has to implement at least one of the
    listed in the hyper-parameter), and produce methods provided (a matching primitive
    has to provide all of the listed in the hyper-parameter).

    Remember that valid values of a hyper-parameter which has primitive values are both
    primitive instances and primitive classes, but the structural type is always just a
    primitive base class. Hyper-parameter values being passed to a primitive which has
    a hyper-parameter expecting primitive(s) should always be primitive instances.

    The default sampling method returns always classes (or a default value, which can be a
    primitive instance), but alternative implementations could sample across instances
    (and for example across also primitive's hyper-parameters).

    Attributes
    ----------
    primitive_families : Sequence[PrimitiveFamily]
        A list of primitive families a matching primitive should be part of.
    algorithm_types : Sequence[PrimitiveAlgorithmType]
        A list of algorithm types a matching primitive should implement at least one.
    produce_methods : Sequence[str]
        A list of produce methods a matching primitive should provide all.
    """

    def __init__(self, default: typing.Type[T], primitive_families: 'typing.Sequence[base.PrimitiveFamily]' = None,  # type: ignore
                 algorithm_types: 'typing.Sequence[base.PrimitiveAlgorithmType]' = None, produce_methods: typing.Sequence[str] = None, *,  # type: ignore
                 semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        if primitive_families is None:
            primitive_families = ()
        if algorithm_types is None:
            algorithm_types = ()
        if produce_methods is None:
            produce_methods = ()

        # Convert any strings to enums.
        self.primitive_families: typing.Tuple[base.PrimitiveFamily, ...] = tuple(base.PrimitiveFamily[primitive_family] for primitive_family in primitive_families)  # type: ignore
        self.algorithm_types: typing.Tuple[base.PrimitiveAlgorithmType, ...] = tuple(base.PrimitiveAlgorithmType[algorithm_type] for algorithm_type in algorithm_types)  # type: ignore
        self.produce_methods = tuple(produce_methods)

        for primitive_family in self.primitive_families:  # type: ignore
            if primitive_family not in list(base.PrimitiveFamily):
                raise exceptions.InvalidArgumentValueError("Unknown primitive family '{primitive_family}'.".format(primitive_family=primitive_family))
        for algorithm_type in self.algorithm_types:  # type: ignore
            if algorithm_type not in list(base.PrimitiveAlgorithmType):
                raise exceptions.InvalidArgumentValueError("Unknown algorithm type '{algorithm_type}'.".format(algorithm_type=algorithm_type))
        for produce_method in self.produce_methods:
            if produce_method != 'produce' and not produce_method.startswith('produce_'):
                raise exceptions.InvalidArgumentValueError("Invalid produce method name '{produce_method}'.".format(produce_method=produce_method))

        self.matching_primitives: typing.Sequence[typing.Union[T, typing.Type[T]]] = None

        # Default value is checked by parent class calling "validate".

        super().__init__(default, semantic_types=semantic_types, description=description)  # type: ignore

    # "all_primitives" is not "Sequence[Type[PrimitiveBase]]" to not introduce an import cycle.
    def populate_primitives(self, all_primitives: typing.Sequence[type] = None) -> None:
        """
        Populate a list of matching primitives.

        Called automatically when needed using `d3m.index` primitives. If this is not desired,
        this method should be called using a list of primitive classes to find matching
        primitives among.

        Parameters
        ----------
        all_primitives : Sequence[Type[PrimitiveBase]]
            An alternative list of all primitive classes to find matching primitives among.
        """

        if all_primitives is None:
            # Importing here to prevent import cycle.
            from d3m import index

            index.load_all()
            all_primitives = index.get_loaded_primitives()  # type: ignore

        matching_primitives = []
        for primitive in all_primitives:
            try:
                self.validate(primitive)
                matching_primitives.append(primitive)
            except (exceptions.InvalidArgumentTypeError, exceptions.InvalidArgumentValueError):
                pass

        default = self.get_default()

        if utils.is_type(default):
            if default not in matching_primitives:
                matching_primitives.append(default)  # type: ignore
        else:
            if type(default) not in matching_primitives:
                matching_primitives.append(default)  # type: ignore
            else:
                matching_primitives[matching_primitives.index(type(default))] = default  # type: ignore

        self.matching_primitives = matching_primitives

    def validate(self, value: typing.Union[T, typing.Type[T]]) -> None:
        # Importing here to prevent import cycle.
        from d3m.primitive_interfaces import base as primitive_interfaces_base

        super().validate(typing.cast(T, value))

        if utils.is_type(value):
            primitive_class = typing.cast(typing.Type[primitive_interfaces_base.PrimitiveBase], value)

            # Additional check that we really have a primitive.
            if not utils.is_subclass(primitive_class, primitive_interfaces_base.PrimitiveBase):
                raise exceptions.InvalidArgumentTypeError("Value '{value}' {for_name}is not a subclass of 'PrimitiveBase' class.".format(
                    value=value, for_name=self._for_name(),
                ))
        else:
            primitive_class = typing.cast(typing.Type[primitive_interfaces_base.PrimitiveBase], type(value))

            # Additional check that we really have a primitive.
            if not utils.is_subclass(primitive_class, primitive_interfaces_base.PrimitiveBase):
                raise exceptions.InvalidArgumentTypeError("Value '{value}' {for_name}is not an instance of 'PrimitiveBase' class.".format(
                    value=value, for_name=self._for_name(),
                ))

        primitive_family = primitive_class.metadata.query()['primitive_family']
        if self.primitive_families and primitive_family not in self.primitive_families:
            raise exceptions.InvalidArgumentValueError(
                "Primitive '{value}' {for_name}has primitive family '{primitive_family}' and not any of: {primitive_families}".format(
                    value=value, for_name=self._for_name(),
                    primitive_family=primitive_family, primitive_families=self.primitive_families,
                )
            )

        algorithm_types = primitive_class.metadata.query()['algorithm_types']
        if self.algorithm_types and set(algorithm_types).isdisjoint(set(self.algorithm_types)):
            raise exceptions.InvalidArgumentValueError(
                "Primitive '{value}' {for_name}has algorithm types '{primitive_algorithm_types}' and not any of: {algorithm_types}".format(
                    value=value, for_name=self._for_name(),
                    primitive_algorithm_types=algorithm_types, algorithm_types=self.algorithm_types,
                )
            )

        produce_methods = {
            method_name for method_name, method_description
            in primitive_class.metadata.query()['primitive_code']['instance_methods'].items()
            if method_description['kind'] == base.PrimitiveMethodKind.PRODUCE
        }
        if not set(self.produce_methods) <= produce_methods:
            raise exceptions.InvalidArgumentValueError(
                "Primitive '{value}' {for_name}has produce methods '{primitive_produce_methods}' and not all of: {produce_methods}".format(
                    value=value, for_name=self._for_name(),
                    primitive_produce_methods=produce_methods, produce_methods=self.produce_methods,
                )
            )

    def sample(self, random_state: RandomState = None) -> typing.Union[T, typing.Type[T]]:  # type: ignore
        """
        Samples a random value from the hyper-parameter search space.

        Returns a random primitive from primitives available through `d3m.index`, by default,
        or those given to a manual call of `populate_primitives`.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        if self.matching_primitives is None:
            self.populate_primitives()

        return random_state.choice(self.matching_primitives)

    def get_max_samples(self) -> typing.Optional[int]:
        if self.matching_primitives is None:
            self.populate_primitives()

        return len(self.matching_primitives)

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[typing.Union[T, typing.Type[T]]]:  # type: ignore
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        It samples primitives available through `d3m.index`, by default,
        or those given to a manual call of `populate_primitives`.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        if self.matching_primitives is None:
            self.populate_primitives()

        size = random_state.randint(min_samples, max_samples + 1)

        return tuple(random_state.choice(self.matching_primitives, size, replace=False))

    def __repr__(self) -> str:
        return '{class_name}(default={default}, primitive_families={primitive_families}, algorithm_types={algorithm_types})'.format(
            class_name=type(self).__name__,
            default=self.get_default(),
            primitive_families=[primitive_family.name for primitive_family in self.primitive_families],  # type: ignore
            algorithm_types=[algorithm_type.name for algorithm_type in self.algorithm_types],  # type: ignore
            produce_methods=list(self.produce_methods),
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()
        structure.update({
            'primitive_families': list(self.primitive_families),
            'algorithm_types': list(self.algorithm_types),
            'produce_methods': list(self.produce_methods),
        })
        return structure

    def value_to_json(self, value: typing.Union[T, typing.Type[T]]) -> typing.Any:
        self.validate(value)

        if utils.is_type(value):
            return {'class': value.metadata.query()['python_path']}  # type: ignore
        else:
            return {'instance': base64.b64encode(pickle.dumps(value)).decode('utf8')}

    def value_from_json(self, json: typing.Any) -> typing.Union[T, typing.Type[T]]:  # type: ignore
        if 'class' in json:
            module_path, name = json['class'].rsplit('.', 1)
            module = importlib.import_module(module_path)
            value = getattr(module, name)
        else:
            # TODO: Limit the types of values being able to load to prevent arbitrary code execution by a malicious pickle.
            value = pickle.loads(base64.b64decode(json['instance'].encode('utf8')))

        self.validate(value)

        return value

    def can_accept_value_type(self, structural_type: typing.Union[type, typing.List[type]]) -> bool:
        if structural_type is typing.Any:
            return True
        elif not super().can_accept_value_type(structural_type):
            return False

        try:
            # We now know that it is a primitive class and we can check other constraints.
            self.validate(typing.cast(typing.Type[T], structural_type))
            return True
        except Exception:
            return False


class Constant(Hyperparameter[T]):
    """
    A constant hyper-parameter that represents a constant default value.

    Type variable ``T`` is optional and if not provided an attempt to
    automatically infer it from ``default`` will be made.
    """

    def validate(self, value: T) -> None:
        super().validate(value)

        default = self.get_default()
        if value != default:
            raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is not the constant default value '{default}'.".format(value=value, for_name=self._for_name(), default=default))


class Bounded(Hyperparameter[T]):
    """
    A bounded hyper-parameter with lower and upper bounds, but no other
    information about the distribution of the space of the hyper-parameter,
    besides a default value.

    Both lower and upper bounds are inclusive. Each bound can be also ``None``
    to signal that the hyper-parameter is unbounded for that bound. Both
    bounds cannot be ``None`` because then this is the same as
    ``Hyperparameter`` class, so you can use that one directly.

    Type variable ``T`` is optional and if not provided an attempt to
    automatically infer it from bounds and ``default`` will be made.

    Attributes
    ----------
    lower : Any
        A lower bound.
    upper : Any
        An upper bound.
    """

    def __init__(self, lower: T, upper: T, default: T, *, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        self.lower = lower
        self.upper = upper

        if self.lower is None and self.upper is None:
            raise exceptions.InvalidArgumentValueError("Lower and upper bounds cannot both be None.")

        # If subclass has not already set it.
        if not hasattr(self, 'structural_type'):
            structural_type = _get_structural_type_argument(self)

            if structural_type == typing.Any:
                structural_types = list(self.infer_type(value) for value in [self.lower, self.upper, default] if value is not None)
                type_util.simplify_for_Union(structural_types)
                structural_type = typing.Union[tuple(structural_types)]  # type: ignore

            self.structural_type = structural_type

        if self.lower is None or self.upper is None:
            maybe_optional_structural_type = typing.cast(type, typing.Optional[self.structural_type])  # type: ignore
        else:
            maybe_optional_structural_type = self.structural_type

        if not self.check_type(self.lower, maybe_optional_structural_type):
            raise exceptions.InvalidArgumentTypeError(
                "Lower bound '{lower}' is not an instance of the structural type: {structural_type}".format(
                    lower=self.lower, structural_type=self.structural_type,
                )
            )

        if not self.check_type(self.upper, maybe_optional_structural_type):
            raise exceptions.InvalidArgumentTypeError(
                "Upper bound '{upper}' is not an instance of the structural type: {structural_type}".format(
                    upper=self.upper, structural_type=self.structural_type,
                ))

        # Default value is checked to be inside bounds by parent class calling "validate".

        super().__init__(default, semantic_types=semantic_types, description=description)

    def validate(self, value: T) -> None:
        super().validate(value)

        # This my throw an exception if value is not comparable, but this is on purpose.
        if self.lower is None:
            if not (value is None or value <= self.upper):  # type: ignore
                raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is outside of range ({lower}, {upper}].".format(
                    value=value, for_name=self._for_name(), lower=self.lower, upper=self.upper,
                ))
        elif self.upper is None:
            if not (value is None or self.lower <= value):  # type: ignore
                raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is outside of range [{lower}, {upper}).".format(
                    value=value, for_name=self._for_name(), lower=self.lower, upper=self.upper,
                ))
        else:
            if not (self.lower <= value <= self.upper):  # type: ignore
                raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is outside of range [{lower}, {upper}].".format(
                    value=value, for_name=self._for_name(), lower=self.lower, upper=self.upper,
                ))

    def validate_default(self) -> None:
        if self.lower is None or self.upper is None:
            maybe_optional_structural_type = typing.cast(type, typing.Optional[self.structural_type])  # type: ignore
        else:
            maybe_optional_structural_type = self.structural_type

        structural_type = self.structural_type
        try:
            self.structural_type = maybe_optional_structural_type
            super().validate_default()
        finally:
            self.structural_type = structural_type

    def sample(self, random_state: RandomState = None) -> T:
        """
        Samples a random value from the hyper-parameter search space.

        It always returns a ``default`` value because the distribution of
        the space is unknown.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        return super().sample(random_state=random_state)

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        It always returns only a ``default`` value because the distribution of
        the space is unknown.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        return super().sample_multiple(min_samples=min_samples, max_samples=max_samples, random_state=random_state)

    def __repr__(self) -> str:
        return '{class_name}(lower={lower}, upper={upper}, default={default})'.format(
            class_name=type(self).__name__,
            lower=self.lower,
            upper=self.upper,
            default=self.get_default(),
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()
        structure.update({
            'lower': self.lower,
            'upper': self.upper,
        })
        return structure


class Enumeration(Hyperparameter[T]):
    """
    An enumeration hyper-parameter with a value drawn uniformly from a list of values.

    If ``None`` is a valid choice, it should be listed among ``values``.

    Type variable ``T`` is optional and if not provided an attempt to
    automatically infer it from ``values`` will be made.

    Attributes
    ----------
    values : Sequence[Any]
        A list of choice values.
    """

    def __init__(self, values: typing.Sequence[T], default: T, *, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        self.values = values

        # If subclass has not already set it.
        if not hasattr(self, 'structural_type'):
            structural_type = _get_structural_type_argument(self)

            if structural_type == typing.Any:
                structural_types = list(self.infer_type(value) for value in self.values)
                type_util.simplify_for_Union(structural_types)
                structural_type = typing.Union[tuple(structural_types)]  # type: ignore

            self.structural_type = structural_type

        for value in self.values:
            if not self.check_type(value, self.structural_type):
                raise exceptions.InvalidArgumentTypeError("Value '{value}' is not an instance of the structural type: {structural_type}".format(value=value, structural_type=self.structural_type))

        # Default value is checked to be among values by parent class calling "validate".

        super().__init__(default, semantic_types=semantic_types, description=description)

    def validate(self, value: T) -> None:
        if value not in self.values:
            raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is not among values.".format(value=value, for_name=self._for_name()))

    def sample(self, random_state: RandomState = None) -> T:
        """
        Samples a random value from the hyper-parameter search space.

        It samples a value from ``values``.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        return random_state.choice(self.values)

    def get_max_samples(self) -> typing.Optional[int]:
        return len(self.values)

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        It samples values from ``values``.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        return tuple(random_state.choice(self.values, size, replace=False))

    def __repr__(self) -> str:
        return '{class_name}(values={values}, default={default})'.format(
            class_name=type(self).__name__,
            values=self.values,
            default=self.get_default(),
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()
        structure.update({
            'values': list(self.values),
        })
        return structure


class UniformBool(Enumeration[bool]):
    """
    A bool hyper-parameter with a value drawn uniformly from ``{True, False}``.
    """

    def __init__(self, default: bool, *, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        super().__init__([True, False], default, semantic_types=semantic_types, description=description)

    def __repr__(self) -> str:
        return '{class_name}(default={default})'.format(
            class_name=type(self).__name__,
            default=self.get_default(),
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()
        del structure['values']
        return structure


class UniformInt(Hyperparameter[int]):
    """
    An int hyper-parameter with a value drawn uniformly from ``[lower, upper)``,
    or from `[lower, upper]``, if the upper bound is inclusive.

    Attributes
    ----------
    lower : int
        A lower bound.
    upper : int
        An upper bound.
    upper_inclusive : bool
        Is the upper bound inclusive?
    """

    def __init__(self, lower: int, upper: int, default: int, *, upper_inclusive: bool = False, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        self.lower = lower
        self.upper = upper
        self.upper_inclusive = upper_inclusive

        # Default value is checked to be inside bounds by parent class calling "validate".

        super().__init__(default, semantic_types=semantic_types, description=description)

    def validate(self, value: int) -> None:
        super().validate(value)

        if self.upper_inclusive:
            if not self.lower <= value <= self.upper:
                raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is outside of range [{lower}, {upper}].".format(
                    value=value, for_name=self._for_name(), lower=self.lower, upper=self.upper,
                ))
        else:
            if not self.lower <= value < self.upper:
                raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is outside of range [{lower}, {upper}).".format(
                    value=value, for_name=self._for_name(), lower=self.lower, upper=self.upper,
                ))

    def sample(self, random_state: RandomState = None) -> int:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        int
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        if self.upper_inclusive:
            return random_state.randint(self.lower, self.upper + 1)
        else:
            return random_state.randint(self.lower, self.upper)

    def get_max_samples(self) -> typing.Optional[int]:
        if self.upper_inclusive:
            return self.upper - self.lower + 1
        else:
            return self.upper - self.lower

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        sample_set: set = set()
        sample_list: list = []
        while len(sample_list) != size:
            value = self.sample(random_state)
            if value not in sample_set:
                sample_set.add(value)
                sample_list.append(value)

        return tuple(sample_list)

    def __repr__(self) -> str:
        return '{class_name}(lower={lower}, upper={upper}, default={default}, upper_inclusive={upper_inclusive})'.format(
            class_name=type(self).__name__,
            lower=self.lower,
            upper=self.upper,
            default=self.get_default(),
            upper_inclusive=self.upper_inclusive,
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()
        structure.update({
            'lower': self.lower,
            'upper': self.upper,
            'upper_inclusive': self.upper_inclusive,
        })
        return structure


class Uniform(Hyperparameter[float]):
    """
    A float hyper-parameter with a value drawn uniformly from ``[lower, upper)``,
    or from `[lower, upper]``, if the upper bound is inclusive.

    If ``q`` is provided, then the value is drawn according to ``round(uniform(lower, upper) / q) * q``.

    Attributes
    ----------
    lower : float
        A lower bound.
    upper : float
        An upper bound.
    q : float
        An optional quantization factor.
    upper_inclusive : bool
        Is the upper bound inclusive?
    """

    def __init__(self, lower: float, upper: float, default: float, q: float = None, *, upper_inclusive: bool = False, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        self.lower = lower
        self.upper = upper
        self.q = q
        self.upper_inclusive = upper_inclusive

        # Default value is checked to be inside bounds by parent class calling "validate".

        super().__init__(default, semantic_types=semantic_types, description=description)

    def validate(self, value: float) -> None:
        super().validate(value)

        if self.upper_inclusive:
            if not self.lower <= value <= self.upper:
                raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is outside of range [{lower}, {upper}].".format(
                    value=value, for_name=self._for_name(), lower=self.lower, upper=self.upper,
                ))
        else:
            if not self.lower <= value < self.upper:
                raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is outside of range [{lower}, {upper}).".format(
                    value=value, for_name=self._for_name(), lower=self.lower, upper=self.upper,
                ))

    def sample(self, random_state: RandomState = None) -> float:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        float
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        if self.upper_inclusive:
            value = random_state.uniform(self.lower, numpy.nextafter(self.upper, self.upper + 1))
        else:
            value = random_state.uniform(self.lower, self.upper)

        if self.q is None:
            return value
        else:
            return numpy.round(value / self.q) * self.q

    def get_max_samples(self) -> typing.Optional[int]:
        return None

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        sample_set: set = set()
        sample_list: list = []
        while len(sample_list) != size:
            value = self.sample(random_state)
            if value not in sample_set:
                sample_set.add(value)
                sample_list.append(value)

        return tuple(sample_list)

    def __repr__(self) -> str:
        return '{class_name}(lower={lower}, upper={upper}, q={q}, default={default}, upper_inclusive={upper_inclusive})'.format(
            class_name=type(self).__name__,
            lower=self.lower,
            upper=self.upper,
            q=self.q,
            default=self.get_default(),
            upper_inclusive=self.upper_inclusive,
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()

        structure.update({
            'lower': self.lower,
            'upper': self.upper,
            'upper_inclusive': self.upper_inclusive,
        })

        if self.q is not None:
            structure['q'] = self.q

        return structure


class LogUniform(Hyperparameter[float]):
    """
    A float hyper-parameter with a value drawn from ``[lower, upper)`` according to ``exp(uniform(log(lower), log(upper)))``
    so that the logarithm of the value is uniformly distributed,
    or from `[lower, upper]``, if the upper bound is inclusive.

    If ``q`` is provided, then the value is drawn according to ``round(exp(uniform(lower, upper)) / q) * q``.

    Attributes
    ----------
    lower : float
        A lower bound.
    upper : float
        An upper bound.
    q : float
        An optional quantization factor.
    upper_inclusive : bool
        Is the upper bound inclusive?
    """

    def __init__(self, lower: float, upper: float, default: float, q: float = None, *, upper_inclusive: bool = False, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        self.lower = lower
        self.upper = upper
        self.q = q
        self.upper_inclusive = upper_inclusive

        # Default value is checked to be inside bounds by parent class calling "validate".

        super().__init__(default, semantic_types=semantic_types, description=description)

    def validate(self, value: float) -> None:
        super().validate(value)

        if self.upper_inclusive:
            if not self.lower <= value <= self.upper:
                raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is outside of range [{lower}, {upper}].".format(
                    value=value, for_name=self._for_name(), lower=self.lower, upper=self.upper,
                ))
        else:
            if not self.lower <= value < self.upper:
                raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}is outside of range [{lower}, {upper}).".format(
                    value=value, for_name=self._for_name(), lower=self.lower, upper=self.upper,
                ))

    def sample(self, random_state: RandomState = None) -> float:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        float
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        if self.upper_inclusive:
            value = numpy.exp(random_state.uniform(numpy.log(self.lower), numpy.log(numpy.nextafter(self.upper, self.upper + 1))))
        else:
            value = numpy.exp(random_state.uniform(numpy.log(self.lower), numpy.log(self.upper)))

        if self.q is None:
            return value
        else:
            return numpy.round(value / self.q) * self.q

    def get_max_samples(self) -> typing.Optional[int]:
        return None

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        sample_set: set = set()
        sample_list: list = []
        while len(sample_list) != size:
            value = self.sample(random_state)
            if value not in sample_set:
                sample_set.add(value)
                sample_list.append(value)

        return tuple(sample_list)

    def __repr__(self) -> str:
        return '{class_name}(lower={lower}, upper={upper}, q={q}, default={default}, upper_inclusive={upper_inclusive})'.format(
            class_name=type(self).__name__,
            lower=self.lower,
            upper=self.upper,
            q=self.q,
            default=self.get_default(),
            upper_inclusive=self.upper_inclusive,
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()

        structure.update({
            'lower': self.lower,
            'upper': self.upper,
            'upper_inclusive': self.upper_inclusive,
        })

        if self.q is not None:
            structure['q'] = self.q

        return structure


class Normal(Hyperparameter[float]):
    """
    A float hyper-parameter with a value drawn normally distributed according to ``mu`` and ``sigma``.

    If ``q`` is provided, then the value is drawn according to ``round(normal(mu, sigma) / q) * q``.

    Attributes
    ----------
    mu : float
        A mean of normal distribution.
    sigma : float
        A standard deviation of normal distribution.
    q : float
        An optional quantization factor.
    """

    def __init__(self, mu: float, sigma: float, default: float, q: float = None, *, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        self.mu = mu
        self.sigma = sigma
        self.q = q

        super().__init__(default, semantic_types=semantic_types, description=description)

    def sample(self, random_state: RandomState = None) -> float:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        float
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        value = random_state.normal(self.mu, self.sigma)

        if self.q is None:
            return value
        else:
            return numpy.round(value / self.q) * self.q

    def get_max_samples(self) -> typing.Optional[int]:
        return None

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        sample_set: set = set()
        sample_list: list = []
        while len(sample_list) != size:
            value = self.sample(random_state)
            if value not in sample_set:
                sample_set.add(value)
                sample_list.append(value)

        return tuple(sample_list)

    def __repr__(self) -> str:
        return '{class_name}(mu={mu}, sigma={sigma}, q={q}, default={default})'.format(
            class_name=type(self).__name__,
            mu=self.mu,
            sigma=self.sigma,
            q=self.q,
            default=self.get_default(),
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()

        structure.update({
            'mu': self.mu,
            'sigma': self.sigma,
        })

        if self.q is not None:
            structure['q'] = self.q

        return structure


class LogNormal(Hyperparameter[float]):
    """
    A float hyper-parameter with a value drawn according to ``exp(normal(mu, sigma))`` so that the logarithm of the value is
    normally distributed.

    If ``q`` is provided, then the value is drawn according to ``round(exp(normal(mu, sigma)) / q) * q``.

    Attributes
    ----------
    mu : float
        A mean of normal distribution.
    sigma : float
        A standard deviation of normal distribution.
    q : float
        An optional quantization factor.
    """

    def __init__(self, mu: float, sigma: float, default: float, q: float = None, *, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        self.mu = mu
        self.sigma = sigma
        self.q = q

        super().__init__(default, semantic_types=semantic_types, description=description)

    def sample(self, random_state: RandomState = None) -> float:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        float
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        value = numpy.exp(random_state.normal(self.mu, self.sigma))

        if self.q is None:
            return value
        else:
            return numpy.round(value / self.q) * self.q

    def get_max_samples(self) -> typing.Optional[int]:
        return None

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        sample_set: set = set()
        sample_list: list = []
        while len(sample_list) != size:
            value = self.sample(random_state)
            if value not in sample_set:
                sample_set.add(value)
                sample_list.append(value)

        return tuple(sample_list)

    def __repr__(self) -> str:
        return '{class_name}(mu={mu}, sigma={sigma}, q={q}, default={default})'.format(
            class_name=type(self).__name__,
            mu=self.mu,
            sigma=self.sigma,
            q=self.q,
            default=self.get_default(),
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()

        structure.update({
            'mu': self.mu,
            'sigma': self.sigma,
        })

        if self.q is not None:
            structure['q'] = self.q

        return structure


class Union(Hyperparameter[T]):
    """
    A union hyper-parameter which combines multiple other hyper-parameters.

    This is useful when a hyper-parameter has multiple modalities and each modality
    can be described with a different hyper-parameter.

    No relation or probability distribution between modalities is prescribed.

    Type variable ``T`` does not have to be specified because the structural type
    can be automatically inferred as a union of all hyper-parameters in configuration.

    This is similar to `Choice` hyper-parameter that it combines hyper-parameters, but
    `Union` combines individual hyper-parameters, while `Choice` combines configurations
    of multiple hyper-parameters.

    Attributes
    ----------
    configuration : FrozenOrderedDict
        A configuration of hyper-parameters to combine into one. It is important
        that configuration uses an ordered dict so that order is reproducible
        (default dict has unspecified order).
    """

    def __init__(self, configuration: 'collections.OrderedDict[str, Hyperparameter]', default: str, *, semantic_types: typing.Sequence[str] = None,
                 description: str = None) -> None:
        if default not in configuration:
            raise exceptions.InvalidArgumentValueError("Default value '{default}' is not in configuration.".format(default=default))

        self.default_hyperparameter = configuration[default]
        self.configuration = frozendict.FrozenOrderedDict(configuration)

        for name, hyperparameter in self.configuration.items():
            if not isinstance(name, str):
                raise exceptions.InvalidArgumentTypeError("Hyper-parameter name is not a string: {name}".format(name=name))
            if not isinstance(hyperparameter, Hyperparameter):
                raise exceptions.InvalidArgumentTypeError("Hyper-parameter description is not an instance of the Hyperparameter class: {name}".format(name=name))

        # If subclass has not already set it.
        if not hasattr(self, 'structural_type'):
            structural_type = _get_structural_type_argument(self)

            if structural_type == typing.Any:
                structural_type = typing.Union[tuple(hyperparameter.structural_type for hyperparameter in self.configuration.values())]  # type: ignore

            self.structural_type = structural_type

        for name, hyperparameter in self.configuration.items():
            if not utils.is_subclass(hyperparameter.structural_type, self.structural_type):
                raise exceptions.InvalidArgumentTypeError(
                    "Hyper-parameter '{name}' is not a subclass of the structural type: {structural_type}".format(
                        name=name, structural_type=self.structural_type,
                    )
                )

        super().__init__(self.configuration[default].get_default(), semantic_types=semantic_types, description=description)

    def contribute_to_class(self, name: str) -> None:
        super().contribute_to_class(name)

        for hyperparameter_name, hyperparameter in self.configuration.items():
            hyperparameter.contribute_to_class('{name}.{hyperparameter_name}'.format(name=self.name, hyperparameter_name=hyperparameter_name))

    def validate(self, value: T) -> None:
        # Check that value belongs to a structural type.
        super().validate(value)

        for name, hyperparameter in self.configuration.items():
            try:
                hyperparameter.validate(value)
                # Value validated with at least one hyper-parameter, we can return.
                return
            except Exception:
                pass

        raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}has not validated with any of configured hyper-parameters.".format(value=value, for_name=self._for_name()))

    def sample(self, random_state: RandomState = None) -> T:
        """
        Samples a random value from the hyper-parameter search space.

        It first chooses a hyper-parameter from its configuration and then
        samples it.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        hyperparameter = random_state.choice(list(self.configuration.values()))

        return hyperparameter.sample(random_state)

    def get_max_samples(self) -> typing.Optional[int]:
        all_max_samples = 0
        for hyperparameter in self.configuration.values():
            hyperparameter_max_samples = hyperparameter.get_max_samples()
            if hyperparameter_max_samples is None:
                return None
            else:
                # TODO: Assumption here is that values between hyper-parameters are independent. What when they are not?
                #       For example, union of UniformInt(0, 10) and UniformInt(5, 15) does not have 20 samples, but only 15 possible.
                all_max_samples += hyperparameter_max_samples

        return all_max_samples

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        sample_set: set = set()
        sample_list: list = []
        while len(sample_list) != size:
            value = self.sample(random_state)
            if value not in sample_set:
                sample_set.add(value)
                sample_list.append(value)

        return tuple(sample_list)

    def __repr__(self) -> str:
        return '{class_name}(configuration={{{configuration}}}, default={default})'.format(
            class_name=type(self).__name__,
            configuration=', '.join('{name}: {hyperparameter}'.format(name=name, hyperparameter=hyperparameter) for name, hyperparameter in self.configuration.items()),
            default=self.get_default(),
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()
        structure.update({
            'configuration': {name: hyperparameter.to_simple_structure() for name, hyperparameter in self.configuration.items()}
        })
        return structure

    def traverse(self) -> 'typing.Iterator[Hyperparameter]':
        yield from super().traverse()

        for hyperparameter in self.configuration.values():
            yield hyperparameter
            yield from hyperparameter.traverse()


class Choice(Hyperparameter[typing.Dict]):
    """
    A hyper-parameter which combines multiple hyper-parameter configurations into one
    hyper-parameter.

    This is useful when a combination of hyper-parameters should exists together.
    Then such combinations can be made each into one choice.

    No relation or probability distribution between choices is prescribed.

    This is similar to `Union` hyper-parameter that it combines hyper-parameters, but
    `Choice` combines configurations of multiple hyper-parameters, while `Union` combines
    individual hyper-parameters.

    Attributes
    ----------
    choices : frozendict
        A map between choices and their classes defining their hyper-parameters configuration.
    """

    def __init__(self, choices: 'typing.Dict[str, typing.Type[Hyperparams]]', default: str, *, semantic_types: typing.Sequence[str] = None,
                 description: str = None) -> None:
        if default not in choices:
            raise exceptions.InvalidArgumentValueError("Default value '{default}' is not among choices.".format(default=default))

        choices = copy.copy(choices)

        for choice, hyperparams in choices.items():
            if not isinstance(choice, str):
                raise exceptions.InvalidArgumentTypeError("Choice is not a string: {choice}".format(choice=choice))
            if not issubclass(hyperparams, Hyperparams):
                raise exceptions.InvalidArgumentTypeError("Hyper-parameters space is not a subclass of 'Hyperparams' class: {choice}".format(choice=choice))
            if 'choice' in hyperparams.configuration:
                raise ValueError("Hyper-parameters space contains a reserved hyper-paramater name 'choice': {choice}".format(choice=choice))

            configuration = collections.OrderedDict(hyperparams.configuration)
            configuration['choice'] = Hyperparameter[str](choice, semantic_types=['https://metadata.datadrivendiscovery.org/types/ChoiceParameter'])

            # We make a copy/subclass adding "choice" hyper-parameter. We add a name suffix to differentiate it from the parent class.
            choices[choice] = hyperparams.define(configuration, class_name='{name}WithChoice'.format(name=hyperparams.__name__), module_name=hyperparams.__module__)

        self.default_hyperparams = choices[default]
        self.choices = frozendict.frozendict(choices)

        # Copy defaults and add "choice".
        defaults = self.choices[default](self.choices[default].defaults(), choice=default)

        # If subclass has not already set it.
        if not hasattr(self, 'structural_type'):
            # Choices do not really have a free type argument, so this is probably the same as "dict".
            self.structural_type = _get_structural_type_argument(self)

        super().__init__(defaults, semantic_types=semantic_types, description=description)

    # We go over all hyper-parameter configurations and set their names. This means that names should not already
    # be set. This is by default so if "Hyperparams.define" is used, but if one defines a custom class,
    # you have to define it like "class MyHyperparams(Hyperparams, set_names=False): ..."
    def contribute_to_class(self, name: str) -> None:
        super().contribute_to_class(name)

        for choice, hyperparams in self.choices.items():
            for hyperparameter_name, hyperparameter in hyperparams.configuration.items():
                hyperparameter.contribute_to_class('{name}.{choice}.{hyperparameter_name}'.format(name=self.name, choice=choice, hyperparameter_name=hyperparameter_name))

    def get_default(self, path: str = None) -> typing.Any:
        if path is None:
            return super().get_default(path)

        if '.' not in path:
            return self.choices[path].defaults()
        else:
            segment, rest = path.split('.', 1)
            return self.choices[segment].defaults(rest)

    def validate(self, value: dict) -> None:
        # Check that value belongs to a structural type, a dict.
        super().validate(value)

        if 'choice' not in value:
            raise exceptions.InvalidArgumentValueError("'choice' is missing in '{value}' {for_name}.".format(value=value, for_name=self._for_name()))

        self.choices[value['choice']].validate(value)

    def sample(self, random_state: RandomState = None) -> dict:
        """
        Samples a random value from the hyper-parameter search space.

        It first chooses a hyper-parameters configuration from available choices and then
        samples it.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        choice = random_state.choice(list(self.choices.keys()))

        sample = self.choices[choice].sample(random_state)

        # The "choice" hyper-parameter should be sampled to its choice value.
        assert choice == sample['choice'], sample

        return sample

    def get_max_samples(self) -> typing.Optional[int]:
        all_max_samples = 0
        for hyperparams in self.choices.values():
            hyperparams_max_samples = hyperparams.get_max_samples()
            if hyperparams_max_samples is None:
                return None
            else:
                all_max_samples += hyperparams_max_samples
        return all_max_samples

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        sample_set: set = set()
        sample_list: list = []
        while len(sample_list) != size:
            value = self.sample(random_state)
            if value not in sample_set:
                sample_set.add(value)
                sample_list.append(value)

        return tuple(sample_list)

    def __repr__(self) -> str:
        return '{class_name}(choices={{{choices}}}, default={default})'.format(
            class_name=type(self).__name__,
            choices=', '.join('{choice}: {hyperparams}'.format(choice=choice, hyperparams=hyperparams) for choice, hyperparams in self.choices.items()),
            default=self.get_default(),
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()
        structure.update({
            'choices': {choice: hyperparams.to_simple_structure() for choice, hyperparams in self.choices.items()}
        })
        return structure

    def value_to_json(self, value: dict) -> typing.Any:
        self.validate(value)

        return self.choices[value['choice']](value).values_to_json_structure()

    def value_from_json(self, json: typing.Any) -> dict:
        value = self.choices[json['choice']].values_from_json_structure(json)

        self.validate(value)

        return value

    def traverse(self) -> 'typing.Iterator[Hyperparameter]':
        yield from super().traverse()

        for hyperparams in self.choices.values():
            yield from hyperparams.traverse()

    def transform_value(self, value: dict, transform: typing.Callable, index: int = 0) -> dict:
        if 'choice' not in value:
            raise exceptions.InvalidArgumentValueError("'choice' is missing in '{value}' {for_name}.".format(value=value, for_name=self._for_name()))

        return self.choices[value['choice']].transform_value(value, transform, index + sorted(self.choices.keys()).index(value['choice']))


# TODO: "elements" hyper-parameter still needs a default. Can we get rid of that somehow? It is not used.
#       Maybe we should require that just top-level hyper-parameter instances need defaults, but not all.
class Set(Hyperparameter[T]):
    """
    A set hyper-parameter which samples multiple times another hyper-parameter or hyper-parameters configuration (elements).

    This is useful when a primitive is interested in more than one value of a hyper-parameter or hyper-parameters configuration.

    Type variable ``T`` does not have to be specified because the structural type
    is a set from provided elements.

    Attributes
    ----------
    elements : Union[Hyperparameter, Type[Hyperparams]]
        A hyper-parameter or hyper-parameters configuration of set elements.
    min_size : int
        A minimal number of elements in the set.
    max_size : int
        A maximal number of elements in the set. Can be ``None`` for no limit.
    is_configuration : bool
        Is ``elements`` a hyper-parameter or hyper-parameters configuration?
    """

    def __init__(self, elements: 'typing.Union[Hyperparameter, typing.Type[Hyperparams]]', default: T, min_size: int = 0, max_size: int = None,
                 *, semantic_types: typing.Sequence[str] = None,
                 description: str = None) -> None:
        self.elements = elements
        self.min_size = min_size
        self.max_size = max_size
        self.is_configuration = utils.is_type(self.elements) and issubclass(typing.cast(type, self.elements), Hyperparams)

        if not isinstance(self.elements, Hyperparameter) and not self.is_configuration:
            raise exceptions.InvalidArgumentTypeError("'elements' argument is not an instance of the Hyperparameter class or a subclass of the Hyperparams class.")

        if not isinstance(self.min_size, int):
            raise exceptions.InvalidArgumentTypeError("'min_size' argument is not an int.")
        if self.min_size < 0:
            raise exceptions.InvalidArgumentValueError("'min_size' cannot be smaller than 0.")
        if self.max_size is not None:
            if not isinstance(self.max_size, int):
                raise exceptions.InvalidArgumentTypeError("'max_size' argument is not an int.")
            if self.min_size > self.max_size:
                raise exceptions.InvalidArgumentValueError("'min_size' cannot be larger than 'max_size'.")

        # If subclass has not already set it.
        if not hasattr(self, 'structural_type'):
            structural_type = _get_structural_type_argument(self)

            if structural_type == typing.Any:
                if self.is_configuration:
                    structural_type = typing.Sequence[self.elements]  # type: ignore
                else:
                    structural_type = typing.Sequence[elements.structural_type]  # type: ignore

            self.structural_type = structural_type

        if not utils.is_subclass(self.structural_type, typing.Sequence):
            raise exceptions.InvalidArgumentTypeError("Structural type is not a subclass of a sequence.")

        elements_type = utils.get_type_arguments(self.structural_type)[typing.T_co]  # type: ignore
        if self.is_configuration:
            if elements_type is not self.elements:
                raise exceptions.InvalidArgumentTypeError("Set's structural type hyper-parameters configuration type.")
        else:
            if elements_type is not elements.structural_type:
                raise exceptions.InvalidArgumentTypeError("Set's structural type does not match elements hyper-parameter's structural type.")

        # Default value is checked by parent class calling "validate".

        super().__init__(default, semantic_types=semantic_types, description=description)

    # We go over the hyper-parameters configuration and set their names. This means that names should not already
    # be set. This is by default so if "Hyperparams.define" is used, but if one defines a custom class,
    # you have to define it like "class MyHyperparams(Hyperparams, set_names=False): ..."
    def contribute_to_class(self, name: str) -> None:
        super().contribute_to_class(name)

        if self.is_configuration:
            for hyperparameter_name, hyperparameter in typing.cast(typing.Type[Hyperparams], self.elements).configuration.items():
                hyperparameter.contribute_to_class('{name}.{hyperparameter_name}'.format(name=self.name, hyperparameter_name=hyperparameter_name))
        else:
            self.elements.contribute_to_class('{name}.elements'.format(name=self.name))

    def get_default(self, path: str = None) -> typing.Any:
        # If "path" is "None" we want to return what was set as a default for this hyper-parameter
        # which might be different than hyper-parameters configuration defaults.
        if path is None or not self.is_configuration:
            return super().get_default(path)
        else:
            return typing.cast(Hyperparams, self.elements).defaults(path)

    def validate(self, value: T) -> None:
        # Check that value belongs to a structural type.
        super().validate(value)

        cast_value = typing.cast(typing.Sequence, value)

        if utils.has_duplicates(cast_value):
            raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}has duplicate elements.".format(value=value, for_name=self._for_name()))

        for v in cast_value:
            self.elements.validate(v)

        if not self.min_size <= len(cast_value):
            raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}has less than {min_size} elements.".format(value=value, for_name=self._for_name(), min_size=self.min_size))
        if self.max_size is not None and not len(cast_value) <= self.max_size:
            raise exceptions.InvalidArgumentValueError("Value '{value}' {for_name}has more than {max_size} elements.".format(value=value, for_name=self._for_name(), max_size=self.max_size))

    def sample(self, random_state: RandomState = None) -> T:
        """
        Samples a random value from the hyper-parameter search space.

        It first randomly chooses the size of the resulting sampled set
        and then samples this number of unique elements.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        return self.elements.sample_multiple(min_samples=self.min_size, max_samples=self.max_size, random_state=random_state)  # type: ignore

    def get_max_samples(self) -> typing.Optional[int]:
        max_samples = self.elements.get_max_samples()
        if max_samples is None:
            return None
        elif self.max_size is None:
            return 2 ** max_samples - sum(scipy_special.comb(max_samples, j, exact=True) for j in range(self.min_size))
        else:
            return sum(scipy_special.comb(max_samples, j, exact=True) for j in range(self.max_size + 1)) - sum(scipy_special.comb(max_samples, j, exact=True) for j in range(self.min_size))

    def sample_multiple(self, min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[T]:
        """
        Samples multiple random values from the hyper-parameter search space. At least ``min_samples``
        of them, and at most ``max_samples``.

        Parameters
        ----------
        min_samples : int
            A minimum number of samples to return.
        max_samples : int
            A maximum number of samples to return.
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Sequence[Any]
            A set (represented as a tuple) of multiple sampled values.
        """

        min_samples, max_samples = self._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        sample_set: set = set()
        sample_list: list = []
        while len(sample_list) != size:
            value = self.sample(random_state)
            if value not in sample_set:
                sample_set.add(value)
                sample_list.append(value)

        return tuple(sample_list)

    def __repr__(self) -> str:
        return '{class_name}(elements={elements}, default={default}, min_size={min_size}, max_size={max_size})'.format(
            class_name=type(self).__name__,
            elements=self.elements,
            default=self.get_default(),
            min_size=self.min_size,
            max_size=self.max_size,
        )

    def to_simple_structure(self) -> typing.Dict:
        structure = super().to_simple_structure()
        structure.update({
            'elements': self.elements.to_simple_structure(),
            'is_configuration': self.is_configuration,
            'min_size': self.min_size,
        })

        if self.max_size is not None:
            structure['max_size'] = self.max_size

        return structure

    def value_to_json(self, value: T) -> typing.Any:
        self.validate(value)

        if self.is_configuration:
            return [typing.cast(typing.Type[Hyperparams], self.elements)(v).values_to_json_structure() for v in typing.cast(typing.Sequence, value)]
        else:
            return [self.elements.value_to_json(v) for v in typing.cast(typing.Sequence, value)]

    def value_from_json(self, json: typing.Any) -> T:
        if self.is_configuration:
            value = typing.cast(T, tuple(typing.cast(typing.Type[Hyperparams], self.elements).values_from_json_structure(j) for j in json))
        else:
            value = typing.cast(T, tuple(self.elements.value_from_json(j) for j in json))

        self.validate(value)

        return value

    def traverse(self) -> 'typing.Iterator[Hyperparameter]':
        yield from super().traverse()

        if self.is_configuration:
            yield from self.elements.traverse()
        else:
            yield self.elements

    def transform_value(self, value: T, transform: typing.Callable, index: int = 0) -> T:
        cast_value = typing.cast(typing.Sequence, value)

        # We assume here that we can make a new instance of the sequence-type used
        # for "value" by providing an iterator of new values to its constructor.
        # This works for tuples which we are using by default to represent a set.
        return type(value)(self.elements.transform_value(v, transform, index + i) for i, v in enumerate(cast_value))  # type: ignore

    def can_accept_value_type(self, structural_type: typing.Union[type, typing.List[type]]) -> bool:
        if not isinstance(structural_type, typing.List):
            # For parent method to return "False" because for "Set" hyper-parameter it has to be a list of types.
            return super().can_accept_value_type(structural_type)

        if not self.min_size <= len(structural_type):
            return False
        if self.max_size is not None and not len(structural_type) <= self.max_size:
            return False

        for st in structural_type:
            if not self.elements.can_accept_value_type(st):
                return False

        return True


class HyperparamsMeta(utils.AbstractMetaclass):
    """
    A metaclass which provides the hyper-parameter description its name.
    """

    def __new__(mcls, class_name, bases, namespace, set_names=True, **kwargs):  # type: ignore
        # This should run only on subclasses of the "Hyperparams" class.
        if bases != (dict,):
            # Hyper-parameters configuration should be deterministic, so order matters.
            configuration = collections.OrderedDict()

            # Create a (mutable) copy and don't modify the input argument.
            namespace = collections.OrderedDict(namespace)

            # We traverse parent classes in order to keep hyper-parameters configuration deterministic.
            for parent_class in bases:
                # Using "isinstance" and not "issubclass" because we are comparing against a metaclass.
                if isinstance(parent_class, mcls):
                    configuration.update(parent_class.configuration)

            for name, value in namespace.items():
                if name.startswith('_'):
                    continue

                if isinstance(value, Hyperparameter):
                    if name in base.STANDARD_PIPELINE_ARGUMENTS or name in base.STANDARD_RUNTIME_ARGUMENTS:
                        raise ValueError("Hyper-parameter name '{name}' is reserved because it is used as an argument in primitive interfaces.".format(
                            name=name,
                        ))

                    if not HYPERPARAMETER_NAME_REGEX.match(name):
                        raise ValueError("Hyper-parameter name '{name}' contains invalid characters.".format(
                            name=name,
                        ))

                    if set_names:
                        value.contribute_to_class(name)

                    configuration[name] = value

            for name in configuration.keys():
                # "name" might came from a parent class, but if not, then remove it
                # from the namespace of the class we are creating.
                if name in namespace:
                    del namespace[name]

            namespace['configuration'] = frozendict.FrozenOrderedDict(configuration)

        return super().__new__(mcls, class_name, bases, namespace, **kwargs)

    def __repr__(self):  # type: ignore
        return '<class \'{module}.{class_name}\' configuration={{{configuration}}}>'.format(
            module=self.__module__,
            class_name=self.__name__,
            configuration=', '.join('{name}: {hyperparameter}'.format(name=name, hyperparameter=hyperparameter) for name, hyperparameter in self.configuration.items()),
        )

    def __setattr__(self, key, value):  # type: ignore
        if key == 'configuration':
            raise AttributeError("Hyper-parameters configuration is immutable.")

        super().__setattr__(key, value)


H = typing.TypeVar('H', bound='Hyperparams')


class Hyperparams(dict, metaclass=HyperparamsMeta):
    """
    A base class to be subclassed and used as a type for ``Hyperparams``
    type argument in primitive interfaces. An instance of this subclass
    is passed as a ``hyperparams`` argument to primitive's constructor.

    You should subclass the class and configure class attributes to
    hyper-parameters you want. They will be extracted out and put into
    the ``configuration`` attribute. They have to be an instance of the
    `Hyperparameter` class for this to happen.

    You can define additional methods and attributes on the class.
    Prefix them with `_` to not conflict with future standard ones.

    When creating an instance of the class, all hyper-parameters have
    to be provided. Default values have to be explicitly passed.

    Attributes
    ----------
    configuration : FrozenOrderedDict
        A hyper-parameters configuration.
    """

    configuration: frozendict.FrozenOrderedDict = frozendict.FrozenOrderedDict()

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        values = dict(*args, **kwargs)

        self.validate(values)

        super().__init__(values)

        self._hash: int = None

    @classmethod
    def sample(cls: typing.Type[H], random_state: RandomState = None) -> H:
        """
        Returns a hyper-parameters sample with all values sampled from their hyper-parameter configurations.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Hyperparams
            An instance of hyper-parameters.
        """
        random_state = sklearn_validation.check_random_state(random_state)

        values = {}

        for name, hyperparameter in cls.configuration.items():
            values[name] = hyperparameter.sample(random_state)

        return cls(values)

    @classmethod
    def get_max_samples(cls) -> typing.Optional[int]:
        hyperparams_max_samples = 1
        for hyperparameter in cls.configuration.values():
            hyperparameter_max_samples = hyperparameter.get_max_samples()
            if hyperparameter_max_samples is None:
                return None
            else:
                # TODO: Assumption here is that hyper-parameters are independent. What when we will support dependencies?
                #       See: https://gitlab.com/datadrivendiscovery/d3m/issues/46
                hyperparams_max_samples *= hyperparameter_max_samples
        return hyperparams_max_samples

    @classmethod
    def _check_sample_size(cls, min_samples: int, max_samples: typing.Optional[int]) -> typing.Tuple[int, int]:
        return check_sample_size(cls, min_samples, max_samples)

    @classmethod
    def sample_multiple(cls: typing.Type[H], min_samples: int = 0, max_samples: int = None, random_state: RandomState = None) -> typing.Sequence[H]:
        min_samples, max_samples = cls._check_sample_size(min_samples, max_samples)

        random_state = sklearn_validation.check_random_state(random_state)

        size = random_state.randint(min_samples, max_samples + 1)

        sample_set: set = set()
        sample_list: list = []
        while len(sample_list) != size:
            value = cls.sample(random_state)
            if value not in sample_set:
                sample_set.add(value)
                sample_list.append(value)

        return tuple(sample_list)

    @classmethod
    def defaults(cls: typing.Type[H], path: str = None) -> typing.Any:
        """
        Returns a hyper-parameters sample with all values set to defaults.

        Parameters
        ----------
        path : str
            An optional path to get defaults for. It can contain ``.`` to represent
            a path through nested hyper-parameters.

        Returns
        -------
        Any
            An instance of hyper-parameters or a default value of a hyper-parameter under ``path``.
        """

        if path is None:
            values = {}

            for name, hyperparameter in cls.configuration.items():
                values[name] = hyperparameter.get_default()

            return cls(values)

        else:
            if '.' not in path:
                return cls.configuration[path].get_default()
            else:
                segment, rest = path.split('.', 1)
                return cls.configuration[segment].get_default(rest)

    @classmethod
    def validate(cls, values: dict) -> None:
        configuration_keys = set(cls.configuration.keys())
        values_keys = set(values.keys())

        missing = configuration_keys - values_keys
        if len(missing):
            raise exceptions.InvalidArgumentValueError("Not all hyper-parameters are specified: {missing}".format(missing=missing))

        extra = values_keys - configuration_keys
        if len(extra):
            raise exceptions.InvalidArgumentValueError("Additional hyper-parameters are specified: {extra}".format(extra=extra))

        for name, value in values.items():
            cls.configuration[name].validate(value)

    @classmethod
    def to_simple_structure(cls) -> typing.Dict:
        """
        Converts the hyper-parameters configuration to a simple structure, similar to JSON, but with values
        left as Python values.

        Returns
        -------
        Dict
            A dict.
        """

        return {name: hyperparameter.to_simple_structure() for name, hyperparameter in cls.configuration.items()}

    @classmethod
    def define(cls: typing.Type[H], configuration: 'collections.OrderedDict[str, Hyperparameter]', *,
               class_name: str = None, module_name: str = None, set_names: bool = False) -> typing.Type[H]:
        """
        Define dynamically a subclass of this class using ``configuration`` and optional
        ``class_name`` and ``module_name``.

        This is equivalent of defining a class statically in Python. ``configuration`` is what
        you would otherwise provide through class attributes.

        Parameters
        ----------
        configuration : OrderedDict[str, Hyperparameter]
             A hyper-parameters configuration.
        class_name : str
            Class name of the subclass.
        module_name : str
            Module name of the subclass.
        set_names : bool
            Should all hyper-parameters defined have their names set. By default ``False``.
            This is different from when defining a static subclass, where the default is ``True``
            and names are set by the default.

        Returns
        -------
        type
            A subclass itself.
        """

        # Create a (mutable) copy and don't modify the input argument.
        namespace: typing.Dict[str, typing.Any] = collections.OrderedDict(configuration)

        if class_name is None:
            # We want automatically generated class names to be unique.
            class_name = '{name}{id}'.format(name=cls.__name__, id=id(configuration))

        if module_name is None:
            frame = inspect.currentframe()
            if frame is not None and frame.f_back is not None:
                module_name = frame.f_back.f_globals['__name__']

        if module_name is not None:
            namespace['__module__'] = module_name

        return types.new_class(class_name, (cls,), {'set_names': set_names}, lambda ns: ns.update(namespace))

    def values_to_json_structure(self) -> typing.Dict[str, typing.Dict]:
        """
        Converts hyper-parameter values to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        return {name: self.configuration[name].value_to_json(value) for name, value in self.items()}

    @classmethod
    def values_from_json_structure(cls: typing.Type[H], json: typing.Dict[str, typing.Dict]) -> H:
        """
        Converts given JSON-compatible structure to an instance of this class with values
        from the structure.

        Parameters
        ----------
        json : Dict
            A JSON-compatible dict.

        Returns
        -------
        Any
            An instance of this class with values from ``json`` argument.
        """

        return cls({name: cls.configuration[name].value_from_json(value) for name, value in json.items()})

    @classmethod
    def traverse(cls) -> typing.Iterator[Hyperparameter]:
        """
        Traverse over all hyper-parameters used in this hyper-parameters configuration.

        Yields
        ------
        Hyperparamater
            The next hyper-parameter used in this hyper-parameters configuration.
        """

        for hyperparameter in cls.configuration.values():
            yield hyperparameter
            yield from hyperparameter.traverse()

    @classmethod
    def transform_value(cls: typing.Type[H], values: dict, transform: typing.Callable, index: int = 0) -> H:
        transformed_values = {}
        for i, name in enumerate(sorted(values.keys())):
            transformed_values[name] = cls.configuration[name].transform_value(values[name], transform, index + i)

        return cls(transformed_values)

    @classmethod
    def can_accept_value_type(cls, structural_type: typing.Union[type, typing.List[type]]) -> bool:
        if structural_type is typing.Any:
            return True
        elif isinstance(structural_type, typing.List):
            # We do not support a list of types. This is used for "Set" hyper-parameter.
            return False
        else:
            return utils.is_subclass(structural_type, cls)

    def replace(self: H, values: typing.Dict[str, typing.Any]) -> H:
        """
        Creates a copy of hyper-parameters with values replaced with values from ``values``.

        This is equivalent of doing ``Hyperparams(hyperparams, **values)``.

        Parameters
        ----------
        values : Dict[str, Any]
            Map between keys and values to replace.

        Returns
        -------
        Hyperparams
            A copy of the object with replaced values.
        """

        return type(self)(self, **values)

    def __setitem__(self, key, value):  # type: ignore
        raise TypeError("Hyper-parameters are immutable.")

    def __delitem__(self, key):  # type: ignore
        raise TypeError("Hyper-parameters are immutable.")

    def clear(self):  # type: ignore
        raise TypeError("Hyper-parameters are immutable.")

    def pop(self, key, default=None):  # type: ignore
        raise TypeError("Hyper-parameters are immutable.")

    def popitem(self):  # type: ignore
        raise TypeError("Hyper-parameters are immutable.")

    def setdefault(self, key, default=None):  # type: ignore
        raise TypeError("Hyper-parameters are immutable.")

    def update(self, *args, **kwargs):  # type: ignore
        raise TypeError("Hyper-parameters are immutable.")

    def __repr__(self) -> str:
        return '{class_name}({super})'.format(class_name=type(self).__name__, super=super().__repr__())

    def __getstate__(self) -> dict:
        return dict(self)

    def __setstate__(self, state: dict) -> None:
        self.__init__(state)  # type: ignore

    # In the past, we had to implement our own __reduce__ method because dict is otherwise pickled
    # using a built-in implementation which does not call "__getstate__". But now we use it also
    # to handle the case of classes defined using "define".
    def __reduce__(self) -> typing.Tuple[typing.Callable, typing.Tuple, dict]:
        # If class has been defined at the global scope of a module, we can use regular pickling approach.
        if _is_defined_at_global_scope(self.__class__):
            return __newobj__, (self.__class__,), self.__getstate__()

        base_cls = None
        define_args_list: typing.List[typing.Dict[str, typing.Any]] = []
        for cls in inspect.getmro(self.__class__):
            if _is_defined_at_global_scope(cls):
                base_cls = cls
                break

            if not issubclass(cls, Hyperparams):
                raise pickle.PickleError("Class is not a subclass of \"Hyperparams\" class.")

            if set(cls.__dict__.keys()) - DEFAULT_HYPERPARAMS_CLASS_ATTRIBUTES:
                raise pickle.PickleError("A class with custom attributes not defined at a global scope.")

            cls = typing.cast(typing.Type[Hyperparams], cls)

            define_args_list.insert(0, {
                'configuration': cls.configuration,
                'class_name': getattr(cls, '__name__', None),
                'module_name': getattr(cls, '__module__', None),
            })

        if base_cls is None:
            raise pickle.PickleError("Cannot find a base class defined at a global scope.")

        if not issubclass(base_cls, Hyperparams):
            raise pickle.PickleError("Found base class is not a subclass of \"Hyperparams\" class.")

        return _recreate_hyperparams_class, (base_cls, define_args_list), self.__getstate__()

    # It is immutable, so hash can be defined.
    def __hash__(self) -> int:
        if self._hash is None:
            h = 0
            for key, value in self.items():
                h ^= hash((key, value))
            self._hash = h
        return self._hash


# This is defined here so that we compute it only once.
DEFAULT_HYPERPARAMS_CLASS_ATTRIBUTES = set(Hyperparams.define(collections.OrderedDict()).__dict__.keys())
