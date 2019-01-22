from typing import Dict, List, Union

Primitive = Union[None, bool, float, int, str]
JSON = Union[Primitive, Dict[str, "JSON"], List["JSON"]]  # type: ignore
