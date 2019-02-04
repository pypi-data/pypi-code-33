from dataclasses import dataclass
from datetime import datetime
from typing import List, Any, Dict
from uuid import UUID


@dataclass
class Cursor:
    id: UUID
    created: datetime


CursorJson = Dict[str, Any]


def mk_cursor(page_size: int, data: List[Any], total=None) -> CursorJson:
    cursor = {"page_size": page_size}
    if total:
        cursor["total"] = total

    if data:
        last = data[-1]
        last_string = f"{last.created_at.isoformat()}|{last.id}"
        cursor["last"] = last_string

    return cursor


def after_to_offset(after) -> Cursor:
    offset = after.split("|")
    dt = datetime.fromisoformat(offset[0])
    id = UUID(offset[1])
    return Cursor(id=id, created=dt)
