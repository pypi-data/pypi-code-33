from typing import (
    TypeVar, Any, Optional, Union, Callable, Iterable, Dict, Tuple, List, Type, IO)

import toml

from collections import OrderedDict
from itertools import chain

from bgez.core import Dictable, Saveable
from bgez.core.inputs import InputType, RawInput
from bgez import logger

__all__ = [
    'KeymapEntry',
    'Keymap',
]

T = TypeVar('T')
F = TypeVar('F', bound=Callable)
Decorator = Callable[[F], F]

def input_value(input: RawInput[T]) -> T:
    return input.value()

class KeymapEntry(RawInput[T]):
    '''
    KeymapEntries are the real process unit for inputs.
    They manage the list of bindings assigned to an action, and perform the
    conversion / merging of the values, based on the input type.
    '''

    def __init__(self, keymap: 'Keymap', name: str, type: Type[InputType[T]], converters: Dict[Type, Callable[[RawInput], T]] = {}):
        self._converters: Dict[Type[InputType[T]], Callable[[RawInput], T]] = converters.copy()
        self._bindings: Dict[str, Callable[[], T]] = OrderedDict()
        self._links: Dict[str, Callable[[], T]] = OrderedDict()
        self._keymap: 'Keymap' = keymap
        self._name: str = name
        self._type = type
        self._input: InputType[T] = type(self)

    def __len__(self):
        '''Number of bindings for this entry.'''
        return len(self._bindings.keys())

    def __contains__(self, binding: str):
        '''Returns if this entry contains `binding`.'''
        binding, _ = self._parse(binding)
        return binding in self._bindings

    def _get_raw_input(self, name: str) -> RawInput:
        return self._keymap.get_raw_input(name)

    def _parse(self, keybinding: str) -> Tuple[str, List[str]]:
        keys = [key.strip() for key in keybinding.split('+')]
        keys.sort()
        return '+'.join(keys), keys

    def _converter(self, input_type: Type[InputType[T]]) -> Callable[[RawInput[T]], T]:
        '''Gets the conversion function(`input_type`) => type(self)'''
        if input_type == self.type:
            return input_value
        try:
            return self._converters[input_type]
        except KeyError:
            ...
        raise TypeError(f'no converters found for {input_type} to {type(self)}')

    def _resolver(self, input: RawInput) -> Callable[[], Any]:
        '''Returns a function that will always return the good input type for `input.value`'''
        return (lambda input, converter:
            lambda: converter(input)
        )(input, self._converter(input.type))

    def link(self, action_name: Union['KeymapEntry', str], linker: Callable[['KeymapEntry'], Any] = input_value) -> None:
        '''Uses `linker` so that `action` contributes to this input.'''
        action: KeymapEntry = self._keymap.get(action_name) \
            if isinstance(action_name, str) else action_name
        self._links[action.name] = lambda: linker(action)

    def value(self) -> T:
        type = self.type
        return type._union(type._filter(
            input() for input in chain(self._links.values(), self._bindings.values())
        ))

    @property
    def name(self) -> str:
        '''The name given by the keymap to this entry.'''
        return self._name

    @property
    def input(self) -> InputType[T]:
        '''The wrapper for this keymap entry.'''
        return self._input

    @property
    def type(self) -> Type[InputType[T]]:
        '''This entry wrapped inside the input type'''
        return self._type

    @property
    def bindings(self) -> Iterable[str]:
        '''Returns the list of bindings for this entry.'''
        return tuple(self._bindings.keys())

    @property
    def links(self) -> Iterable[str]:
        '''Returns the list of linked actions to this entry.'''
        return tuple(self._links.keys())

    def set(self, bindings: Iterable[str]) -> None:
        '''Sets the bindings for this entry.'''
        self._bindings.clear()
        self.add(*bindings)

    def add(self, *bindings: str) -> None:
        '''Adds `bindings` to this entry.'''
        for binding in bindings:
            binding, keys = self._parse(binding)

            resolvers = [self._resolver(self._get_raw_input(key))
                for key in keys]

            state = (lambda resolvers, intersection, filter: # hmmm
                lambda: intersection(filter(resolver() for resolver in resolvers))
            )(resolvers, self.type._intersection, self.type._filter)

            self._bindings[binding] = state

    def remove(self, *bindings: str) -> None:
        '''Removes `bindings` from this entry.'''
        for binding in bindings:
            binding, _ = self._parse(binding)
            del self._bindings[binding]

class Keymap(Dictable, Saveable):
    '''
    Keymaps make the link between `actions` and `keybindings`.
    This is the high level abstraction for input management.
    '''

    def __init__(self, registry: Dict[str, RawInput], *, defaults: Dict[str, Iterable[str]] = {}):
        self._defaults: Dict[str, Iterable[str]] = defaults.copy()
        self._mappings: Dict[str, KeymapEntry] = OrderedDict()
        self._registry: Dict[str, RawInput] = registry

    def __contains__(self, action):
        '''Returns if `action` is defined for this keymap.'''
        return action in self._mappings

    def __getitem__(self, action):
        '''Returns the `KeymapEntry` for the action.'''
        return self.get(action)

    def _resolve_path(self, path: str) -> str:
        return path

    @property
    def actions(self) -> Iterable[str]:
        '''Returns the list of registered actions.'''
        return tuple(self._mappings.keys())

    def get_raw_input(self, name: str) -> RawInput:
        '''Returns the input from the registry for `name`.'''
        return self._registry[name]

    def define(self, action: str, type: Type[InputType[T]], *, converters={}, default=[]) -> KeymapEntry[T]:
        '''
        Defines an action and the type of expected value.\n
        - `action`: name of the action to define.
        - `type`: the type of expected values.
        - `converters`: the map of incompatible types -> conversion function.
        - `default`: the default bindings if not defined in the config.
        '''
        if action in self: raise ValueError(f'"{action}" is already defined')
        self._mappings[action] = entry = KeymapEntry(self, action, type, converters)
        bindings = self._defaults[action] = default.copy()
        entry.set(bindings)
        return entry

    def link(self, action: Union[RawInput, str], sub_action: Union[RawInput, str], linker: Callable[[Any], Any] = None) -> Optional[Decorator]:
        '''Creates a link between two actions.'''
        def decorator(linker):
            nonlocal action, sub_action
            if isinstance(sub_action, str):
                sub_action = self._mappings[sub_action]
            if isinstance(action, str):
                action = self._mappings[action]
            action.link(sub_action, linker)
        if linker is None:
            return decorator
        decorator(linker)
        return None

    def get(self, action: str) -> KeymapEntry:
        '''Returns the `KeymapEntry` for the action.'''
        return self._mappings[action]

    def set(self, action: str, keybindings: Iterable[str]) -> None:
        '''Sets the bindings for `action`.'''
        self.get(action).set(keybindings)

    def add(self, action: str, *keybindings: str) -> None:
        '''Adds a keybinding for the action.'''
        self.get(action).add(*keybindings)

    def remove(self, action: str, *keybindings: str) -> None:
        '''Removes a keybinding from an action.'''
        self.get(action).remove(*keybindings)

    def typeof(self, action: str) -> Type[InputType]:
        '''Returns the associated type for `action`.'''
        return self.get(action).type

    def valueof(self, action: str) -> Any:
        '''Returns the value for a given action.'''
        return self.get(action).value()

    def to_dict(self) -> dict:
        defaulted = self._defaults.copy()
        defaulted.update({
            action: entry.bindings
            for action, entry in self._mappings.items()
        })
        return defaulted

    def from_dict(self, data: dict) -> None:
        defaulted: Dict[str, Iterable[str]] = self._defaults.copy()
        defaulted.update(data)

        for action, bindings in defaulted.items():
            if action in self:
                self.set(action, bindings)
            else:
                logger.warning('"%s" is not defined in %s', action, self)

    def save(self, path: str, *, opener: Callable[[str, str], IO] = open) -> None:
        resolved_path = self._resolve_path(path)
        with opener(resolved_path, 'w') as file:
            toml.dump({
                'actions': self.to_dict(),
                # 'metadata': {},
            }, file)

    def load(self, path: str, *, opener: Callable[[str, str], IO] = open) -> None:
        resolved_path = self._resolve_path(path)
        try:
            with opener(resolved_path, 'r') as file:
                data = toml.load(file)
        except FileNotFoundError:
            logger.info('file "%s" doesn\'t exist, using default keymap bindings', path)
            data = {}

        self.from_dict(data.get('actions', {}))
        self.save(path, opener=opener)
