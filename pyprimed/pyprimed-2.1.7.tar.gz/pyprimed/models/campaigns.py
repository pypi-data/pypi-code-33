from .base import SimpleCollection
from .campaign import Campaign


class Campaigns(SimpleCollection):
    _RESOURCE = Campaign
    _DEFAULT_SORTING = ["name", "ASC"]
    _DEFAULT_RANGE = [0, 100]
