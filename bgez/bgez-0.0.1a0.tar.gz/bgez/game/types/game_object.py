from typing import Any, Optional, Union, Iterable, Iterator, List, Tuple, NamedTuple

from bgez.core.sentinel import Sentinel
from bgez.core import CallbackList, undefined

from . import wrapper as _wrapper
from . import scene as _scene

from bgez.stubs import mathutils
from bge.types import (
    KX_BatchGroup,
    KX_BoundingBox,
    KX_CollisionContactPoint,
    KX_GameObject,
    KX_LodManager,
    KX_Mesh,
    KX_PolyProxy,
    KX_PythonComponent,
)

__all__ = [
    'GameObject',
    'CollisionEvent',
    'RayCastHitEvent',
]

class CollisionEvent(NamedTuple):
    object: Optional['GameObject']
    point: mathutils.Vector
    normal: mathutils.Vector
    points: List[mathutils.Vector]

class RayCastHitEvent(NamedTuple):
    object: Optional['GameObject']
    position: mathutils.Vector
    normal: mathutils.Vector
    polygon: Optional[KX_PolyProxy] = None
    uv: Optional[Tuple[float, float]] = None

class GameProperties:

    owner: 'GameObject'

    def __init__(self, gameobject: 'GameObject'):
        self.owner = gameobject

    def __str__(self):
        return str(self.copy())

    def __contains__(self, key) -> bool:
        return key in self.owner._pyobject

    def __iter__(self) -> Iterator:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self.keys())

    def __getitem__(self, key) -> Any:
        return self.owner._pyobject.get(key)

    def __setitem__(self, key, item) -> None:
        self.owner._pyobject[key] = item

    def __delitem__(self, key) -> None:
        del self.owner._pyobject[key]

    def keys(self) -> List:
        return self.owner._pyobject.getPropertyNames()

    def values(self) -> Iterable:
        return [self.owner._pyobject.get(key) for key in self.keys()]

    def items(self) -> Iterable[Tuple[Any, Any]]:
        return [(key, self.owner._pyobject.get(key)) for key in self.keys()]

    def get(self, key, default=undefined) -> Any:
        if default is undefined:
            return self.owner._pyobject.get(key)
        return self.owner._pyobject.get(key, default)

    def setdefault(self, key, default) -> Any:
        if key not in self:
            self[key] = default
        return self.get(key)

    def update(self, other: dict) -> None:
        for key, value in other.items():
            self[key] = value

    def copy(self) -> dict:
        return dict(self.items())

    def clear(self):
        for key in self.keys():
            del self[key]

    def pop(self, key, default=undefined):
        if key in self:
            value = self.get(key)
            del self[key]
            return value

        elif default is undefined:
            raise KeyError(key)

        return default

    def popitem(self):
        keys = self.keys()
        if len(keys) == 0:
            raise ValueError('empty')
        key = keys[-1]
        return key, self.pop(key)

@_wrapper.register_wrapper(KX_GameObject)
class GameObject(_wrapper.PyObjectPlus):

    _pyobject: KX_GameObject
    __properties: 'GameProperties'

    def __init__(self, kx_game_object: KX_GameObject):
        super().__init__(kx_game_object)
        self.__properties = GameProperties(self)
        self.__hook()

    def __hook(self):
        kx_game_object = self._pyobject

        self.ending = CallbackList()
        kx_game_object[Sentinel] = Sentinel(self.ending.__call__)

        self.collision = CallbackList()
        if self.physics_id > 0: # avoid undefined physics controller
            kx_game_object.collisionCallbacks = [
                lambda object, point, normal, points:
                    self.collision(CollisionEvent(object, point, normal, points))]

    def __str__(self):
        return f'{self.__class__.__qualname__}({self.name})'

    @property
    def properties(self) -> 'GameProperties':
        return self.__properties

    @property
    def library(self) -> str:
        return self.properties['__library__']

    @library.setter
    def library(self, value: str):
        if '__library__' in self.properties:
            raise ValueError('cannot reset an object\'s library')
        self.properties['__library__'] = value

    def end(self) -> None:
        self._pyobject.endObject()

    def replace_mesh(self, mesh: KX_Mesh, display: bool = True, physics: bool = False) -> None:
        self._pyobject.replace_mesh(mesh, display, physics)

    def align_axis_to(self, vector: mathutils.Vector, axis: int = 2, factor: float = 1.) -> None:
        self._pyobject.alignAxisToVect(vector, axis, factor)

    def local_to_world(self, vector: mathutils.Vector) -> mathutils.Vector:
        return self._pyobject.getAxisVect(vector)

    def apply_movement(self, movement: mathutils.Vector, *, local: bool = False) -> None:
        self._pyobject.applyMovement(movement, local)

    def apply_rotation(self, rotation: mathutils.Vector, *, local: bool = False) -> None:
        self._pyobject.applyRotation(rotation, local)

    def apply_force(self, force: mathutils.Vector, *, local: bool = False) -> None:
        self._pyobject.applyForce(force, local)

    def apply_torque(self, torque: mathutils.Vector, *, local: bool = False) -> None:
        self._pyobject.applyTorque(torque, local)

    def apply_impulse(self, point: mathutils.Vector, impulse: mathutils.Vector, *, local: bool = False) -> None:
        self._pyobject.applyImpulse(point, impulse, local)

    def suspend_physics(self, *, free_constraints: bool = False) -> None:
        self._pyobject.suspendPhysics(free_constraints)

    def restore_physics(self) -> None:
        self._pyobject.restorePhysics()

    def suspend_dynamics(self, *, ghost: bool = False) -> None:
        self._pyobject.suspendDynamics(ghost)

    def restore_dynamics(self) -> None:
        self._pyobject.restoreDynamics()

    def enable_rigidbody(self) -> None:
        self._pyobject.enableRigidBody()

    def disable_rigidbody(self) -> None:
        self._pyobject.disableRigidBody()

    def distance_to(self, other: Union['GameObject', mathutils.Vector]) -> float:
        if isinstance(other, GameObject):
            other = other._pyobject
        return self._pyobject.getDistanceTo(other)

    def vector_to(self, other: Union['GameObject', mathutils.Vector]) -> Tuple[float, mathutils.Vector, mathutils.Vector]:
        if isinstance(other, GameObject):
            other = other._pyobject
        return self._pyobject.getVectTo(other)

    def raycast_to(self, other: Union['GameObject', mathutils.Vector], *, distance: float = 0, property: str = '') -> Optional['GameObject']:
        if isinstance(other, GameObject):
            other = other._pyobject
        return _wrapper.wrap(
            self._pyobject.rayCastTo(other, distance, property))

    def raycast(self, *,
        start: Union['GameObject', mathutils.Vector] = None, end: Union['GameObject', mathutils.Vector] = None,
        distance: float = 0, property: str = '', face: bool = False, xray: bool = False,
        polygon: int = 0, mask: int = 0xffff
    ) -> RayCastHitEvent:

        if isinstance(start, GameObject):
            start = start._pyobject
        if isinstance(end, GameObject):
            end = end._pyobject

        object, *rest = self._pyobject.rayCast(
            end, start, distance, property, face, xray, polygon, mask)
        object = _wrapper.wrap(object)

        if polygon + 2 == len(rest):
            return RayCastHitEvent(object, *rest)
        raise ValueError

    def collides(self, other: 'GameObject') -> Tuple[bool, List[KX_CollisionContactPoint]]:
        if isinstance(other, GameObject):
            other = other._pyobject
        return self._pyobject.collide(other)

    def set_collision_margin(self, margin: float) -> None:
        self._pyobject.setCollisionMargin(margin)

    def reinstance_physics_mesh(self, *, object: 'GameObject' = None, mesh: KX_Mesh = None, duplicate: bool = False) -> bool:
        if isinstance(object, GameObject):
            object = object._pyobject
        return self._pyobject.reinstancePhysicsMesh(object, mesh, duplicate)

    def replace_physics_mesh(self, object: 'GameObject') -> None:
        if isinstance(object, GameObject):
            object = object._pyobject
        self._pyobject.replacePhysicsMesh(object)

    @property
    def name(self) -> str:
        return self._pyobject.name

    @property
    def mass(self) -> float:
        return self._pyobject.mass

    @mass.setter
    def mass(self, value: float):
        self._pyobject.mass = value

    @property
    def is_dynamics_suspended(self) -> bool:
        return self._pyobject.isDynamicsSuspended

    @property
    def linear_damping(self) -> float:
        return self._pyobject.linearDamping

    @linear_damping.setter
    def linear_damping(self, value: float):
        self._pyobject.linearDamping = value

    @property
    def angular_damping(self) -> float:
        return self._pyobject.angularDamping

    @angular_damping.setter
    def angular_damping(self, value: float):
        self._pyobject.angularDamping = value

    @property
    def local_inertia(self) -> mathutils.Vector:
        return self._pyobject.localInertia

    @local_inertia.setter
    def local_inertia(self, value: mathutils.Vector):
        self._pyobject.localInertia = value

    @property
    def group_members(self) -> Optional['_wrapper.ListValue']:
        return _wrapper.wrap(self._pyobject.groupMembers)

    @property
    def group_object(self) -> Optional['GameObject']:
        return _wrapper.wrap(self._pyobject.groupObject)

    @property
    def collison_group(self) -> int:
        '''
        16-bitmask representing the collision layers this object belongs to.
        '''
        return self._pyobject.collisionGroup

    @collison_group.setter
    def collison_group(self, value: int):
        self._pyobject.collisionGroup = value

    @property
    def collision_mask(self) -> int:
        '''
        16-bitmask representing the collision layers this object can interact with.
        '''
        return self._pyobject.collisionMask

    @collision_mask.setter
    def collision_mask(self, value: int):
        self._pyobject.collisionMask = value

    @property
    def physics_id(self):
        return self._pyobject.getPhysicsId()

    @property
    def scene(self) -> '_scene.Scene':
        return _wrapper.wrap(self._pyobject.scene)

    @property
    def parent(self) -> 'Optional[GameObject]':
        parent = self._pyobject.parent
        if parent is None: return None
        return _wrapper.wrap(parent)

    @parent.setter
    def parent(self, parent):
        self._pyobject.setParent(parent)

    @property
    def visible(self) -> bool:
        return self._pyobject.visible

    @visible.setter
    def visible(self, value):
        self._pyobject.visible = True

    @property
    def layer(self) -> int:
        '''
        16-bitmask shadow layer.
        '''
        return self._pyobject.layer

    @layer.setter
    def layer(self, value):
        self._pyobject.layer = value

    @property
    def culling_box(self) -> KX_BoundingBox:
        return self._pyobject.cullingBox

    @property
    def culled(self) -> bool:
        return self._pyobject.culled

    @property
    def color(self) -> mathutils.Vector:
        return self._pyobject.color

    @color.setter
    def color(self, value):
        self._pyobject.color = value

    @property
    def occlusion(self) -> bool:
        return self._pyobject.occlusion

    @occlusion.setter
    def occlusion(self, value):
        self._pyobject.occlusion = value

    @property
    def physics_culling(self) -> bool:
        return self._pyobject.physicsCulling

    @physics_culling.setter
    def physics_culling(self, value):
        self._pyobject.physicsCulling = value

    @property
    def logic_culling(self) -> bool:
        return self._pyobject.physicsCulling

    @logic_culling.setter
    def logic_culling(self, value):
        self._pyobject.physicsCulling = value

    @property
    def physics_culling_radius(self) -> float:
        return self._pyobject.physicsCullingRadius

    @physics_culling_radius.setter
    def physics_culling_radius(self, value):
        self._pyobject.physicsCullingRadius = value

    @property
    def logic_culling_radius(self) -> float:
        return self._pyobject.logicCullingRadius

    @logic_culling_radius.setter
    def logic_culling_radius(self, value):
        self._pyobject.logicCullingRadius = value

    @property
    def world_position(self) -> mathutils.Vector:
        return self._pyobject.worldPosition

    @world_position.setter
    def world_position(self, value):
        self._pyobject.worldPosition = value

    @property
    def local_position(self) -> mathutils.Vector:
        return self._pyobject.localPosition

    @local_position.setter
    def local_position(self, value):
        self._pyobject.localPosition = value

    @property
    def world_orientation(self) -> mathutils.Matrix:
        return self._pyobject.worldOrientation

    @world_orientation.setter
    def world_orientation(self, value):
        self._pyobject.worldOrientation = value

    @property
    def local_orientation(self) -> mathutils.Matrix:
        return self._pyobject.localOrientation

    @local_orientation.setter
    def local_orientation(self, value):
        self._pyobject.localOrientation = value

    @property
    def world_scale(self) -> mathutils.Vector:
        return self._pyobject.worldScale

    @world_scale.setter
    def world_scale(self, value):
        self._pyobject.worldScale = value

    @property
    def local_scale(self) -> mathutils.Vector:
        return self._pyobject.localScale

    @local_scale.setter
    def local_scale(self, value):
        self._pyobject.localScale = value

    @property
    def world_transform(self) -> mathutils.Matrix:
        return self._pyobject.worldTransform

    @world_transform.setter
    def world_transform(self, value):
        self._pyobject.worldTransform = value

    @property
    def local_transform(self) -> mathutils.Matrix:
        return self._pyobject.localTransform

    @local_transform.setter
    def local_transform(self, value):
        self._pyobject.localTransform = value

    @property
    def world_linear_velocity(self) -> mathutils.Vector:
        return self._pyobject.worldLinearVelocity

    @world_linear_velocity.setter
    def world_linear_velocity(self, value):
        self._pyobject.worldLinearVelocity = value

    @property
    def local_linear_velocity(self) -> mathutils.Vector:
        return self._pyobject.localLinearVelocity

    @local_linear_velocity.setter
    def local_linear_velocity(self, value):
        self._pyobject.localLinearVelocity = value

    @property
    def world_angular_velocity(self) -> mathutils.Vector:
        return self._pyobject.worldAngularVelocity

    @world_angular_velocity.setter
    def world_angular_velocity(self, value):
        self._pyobject.worldAngularVelocity = value

    @property
    def local_angular_velocity(self) -> mathutils.Vector:
        return self._pyobject.localAngularVelocity

    @local_angular_velocity.setter
    def local_angular_velocity(self, value):
        self._pyobject.localAngularVelocity = value

    @property
    def gravity(self) -> mathutils.Vector:
        return self._pyobject.gravity

    @gravity.setter
    def gravity(self, value):
        self._pyobject.gravity = value

    @property
    def time_offset(self) -> float:
        return self._pyobject.timeOffset

    @time_offset.setter
    def time_offset(self, value):
        self._pyobject.timeOffset = value

    @property
    def state(self) -> int:
        '''
        16-bitmask representing the logic state of the object.
        '''
        return self._pyobject.state

    @state.setter
    def state(self, value):
        self._pyobject.state = value

    @property
    def meshes(self) -> List[KX_Mesh]:
        return self._pyobject.meshes

    @property
    def batch_group(self) -> KX_BatchGroup:
        return self._pyobject.batchGroup

    @property
    def sensors(self) -> List[Any]:
        return self._pyobject.sensors

    @property
    def controllers(self) -> List[Any]:
        return self._pyobject.controllers

    @property
    def actuators(self) -> List[Any]:
        return self._pyobject.actuators

    @property
    def components(self) -> List[KX_PythonComponent]:
        return self._pyobject.components

    @property
    def children(self) -> '_wrapper.ListValue':
        return _wrapper.wrap(self._pyobject.children)

    @property
    def children_recursive(self) -> '_wrapper.ListValue':
        return _wrapper.wrap(self._pyobject.childrenRecursive)

    @property
    def life(self) -> float:
        return self._pyobject.life

    @property
    def debug(self) -> bool:
        return self._pyobject.debug

    @property
    def debug_recursive(self) -> bool:
        return self._pyobject.debugRecursive

    @property
    def current_lod_level(self) -> int:
        return self._pyobject.currentLodLevel

    @property
    def lod_manager(self) -> KX_LodManager:
        return self._pyobject.lodManager
