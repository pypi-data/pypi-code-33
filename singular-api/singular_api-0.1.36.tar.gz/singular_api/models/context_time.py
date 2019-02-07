from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin,
        )

from .context import Context


class ContextTime(
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin
        ):
    COMPLEX_FIELDS = {}
    TRANSLATE_BY_ID = (
        "context"
    )
    RO_FIELDS = (
        "id",
        )
    W_FIELDS = (
        "base_intervals",
        "context",
        "active_from",
        "active_until",
        "duration",
        "excluding",
        "start"
        )
    FIELDS = RO_FIELDS + W_FIELDS

    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id, client, dictionary)
