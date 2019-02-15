'''Contains the ContainerDefinition and Container classes.'''
from typing import (Any, Callable, MutableMapping, Sequence)

class Container:
  '''DependencyInjection container instance.'''
  def __init__(self, container_definition: 'ContainerDefinition') -> None:
    self.container_definition = container_definition
    self.services: MutableMapping[str, Any] = {}

  def has(self, key: str) -> bool:
    return key in self.services

  def get(self, key: str) -> Any:
    if key not in self.services:
      self.services[key] = self.container_definition.get(key)(self)
    return self.services[key]

  def reset(self, key: str) -> 'Container':
    del self.services[key]
    return self

  def reset_all(self) -> 'Container':
    self.services = {}
    return self

Factory = Callable[[Container], Any]

class ContainerDefinition:
  '''Maps dependency keys to factories.'''
  def __init__(self, *, allow_overwrite: bool = False) -> None:
    self.allow_overwrite: bool = allow_overwrite
    self.services: MutableMapping[str, Factory] = {}

  def add(self, key: str, factory: Factory) -> 'ContainerDefinition':
    '''Map a key to a factory.'''
    if not self.allow_overwrite:
      if key in self.services:
        raise KeyError(f'Key {key} already added to container')
    self.services[key] = factory
    return self

  def add_service(
      self,
      key: str,
      dependencies: Sequence[str],
      factory: Callable,
  ) -> 'ContainerDefinition':
    '''Simple method to add a service that depends only on things defined in the container.'''
    return self.add(key, _service(dependencies, factory))

  def get(self, key: str) -> Factory:
    return self.services[key]

  def get_container(self) -> Container:
    return Container(self)

def _service(dependencies: Sequence[str], factory: Callable) -> Factory:
  def build(container: Container) -> Any:
    return factory(*[container.get(key) for key in dependencies])
  return build
