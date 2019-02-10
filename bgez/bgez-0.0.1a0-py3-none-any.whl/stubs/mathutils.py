from typing import Any, Union, Optional, Tuple

__all__ = [
    'Vector',
    'Euler',
    'Color',
    'Quaternion',
    'Matrix',
]

class Vector:

    owner: Optional[Any]

    x: float
    y: float
    z: float
    w: float

    xy: 'Vector'
    yz: 'Vector'
    xz: 'Vector'
    xyz: 'Vector'

    length: float
    length_squared: float
    magnitude: float

    is_frozen: bool
    is_wrapped: bool

    def angle(self, other: 'Vector', fallback: float = None) -> float:
        ...

    def angle_signed(self, other: 'Vector', fallback: float) -> float:
        ...

    def copy(self) -> 'Vector':
        ...

    def cross(self, other: 'Vector') -> Union['Vector', float]:
        ...

    def dot(self, other: 'Vector') -> float:
        ...

    def freeze(self) -> 'Vector':
        ...

    def lerp(self, other: 'Vector') -> 'Vector':
        ...

    def negate(self) -> 'Vector':
        ...

    def normalize(self) -> None:
        ...

    def normalized(self) -> 'Vector':
        ...

    def orthogonal(self) -> 'Vector':
        ...

    def project(self, other: 'Vector') -> 'Vector':
        ...

    def reflect(self, mirror: 'Vector') -> 'Vector':
        ...

    def resize(self, size=3) -> None:
        ...

    def resize_2d(self) -> None:
        ...

    def resize_3d(self) -> None:
        ...

    def resize_4d(self) -> None:
        ...

    def resized(self, size=3) -> 'Vector':
        ...

    def rotate(self, other: Union['Vector', 'Quaternion', 'Matrix']) -> None:
        ...

    def rotation_difference(self, other: 'Vector') -> 'Quaternion':
        ...

    def slerp(self, other: 'Vector', factor: float, fallback: 'Vector' = None) -> 'Vector':
        ...

    def to_2d(self) -> 'Vector':
        ...

    def to_3d(self) -> 'Vector':
        ...

    def to_4d(self) -> 'Vector':
        ...

    def to_track_quat(self, track: str, up: str) -> 'Quaternion':
        ...

    def to_tuple(self, precision: int = -1) -> Tuple[float, float, float, float]:
        ...

    def zero(self) -> None:
        ...

class Euler(Vector):
    ...

class Color(Vector):
    ...

class Quaternion:

    owner: Optional[Any]

    x: float
    y: float
    z: float
    w: float

    angle: float
    vector: 'Vector'
    magnitude: float

    is_frozen: bool
    is_wrapped: bool

    def conjugate(self) -> None:
        ...

    def conjugated(self) -> 'Quaternion':
        ...

    def copy(self) -> 'Quaternion':
        ...

    def cross(self, other: 'Quaternion') -> 'Quaternion':
        ...

    def dot(self, other: 'Quaternion') -> 'Quaternion':
        ...

    def freeze(self) -> None:
        ...

    def identity(self) -> 'Quaternion':
        ...

    def invert(self) -> None:
        ...

    def negate(self) -> 'Quaternion':
        ...

    def normalize(self) -> None:
        ...

    def normalized(self) -> 'Quaternion':
        ...

    def rotate(self, other: Union['Euler', 'Quaternion', 'Matrix']) -> None:
        ...

    def rotation_difference(self, other: 'Quaternion') -> 'Quaternion':
        ...

    def slerp(self, other: 'Quaternion', factor: float) -> 'Quaternion':
        ...

    def to_axis_angle(self) -> Tuple['Vector', float]:
        ...

    def to_euler(self, order: str, euler_compat: 'Euler' = None):
        ...

    def to_exponential_map(self) -> 'Vector':
        ...

    def to_matrix(self) -> 'Matrix':
        ...

class Matrix:

    owner: Optional[Any]
    col: Any
    row: Any

    median_scale: float

    is_frozen: bool
    is_negative: bool
    is_orthogonal: bool
    is_orthogonal_axis_vectors: bool
    is_wrapped: bool

    def adjugate(self) -> None:
        ...

    def adjugated(self) -> 'Matrix':
        ...

    def copy(self) -> 'Matrix':
        ...

    def decompose(self) -> Tuple['Vector', 'Quaternion', 'Vector']:
        ...

    def determinant(self) -> float:
        ...

    def freeze(self) -> 'Matrix':
        ...

    def identity(self) -> None:
        ...

    def invert(self, fallback: 'Matrix' = None) -> None:
        ...

    def invert_safe(self) -> None:
        ...

    def inverted(self, fallback: 'Matrix' = None) -> 'Matrix':
        ...

    def inverted_safe(self) -> 'Matrix':
        ...

    def lerp(self, other: 'Matrix', factor: float) -> 'Matrix':
        ...

    def normalize(self) -> None:
        ...

    def normalized(self) -> 'Matrix':
        ...

    def resize_4x4(self) -> None:
        ...

    def rotate(self, other: Union['Euler', 'Quaternion', 'Matrix']) -> None:
        ...

    def to_3x3(self) -> 'Matrix':
        ...

    def to_4x4(self) -> 'Matrix':
        ...

    def to_euler(self) -> 'Euler':
        ...

    def to_scale(self) -> 'Vector':
        ...

    def to_translation(self) -> 'Vector':
        ...

    def transpose(self) -> None:
        ...

    def transposed(self) -> 'Matrix':
        ...

    def zero(self) -> 'Matrix':
        ...
