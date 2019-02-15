from enum import Enum


class event_ids(Enum):
    ONBOARDING_REQUEST = 1
    ONBOARDING_RESPONSE = 2
    REGULAR_MESSAGE = 3
    OFFBOARDING = 4
    TIMEOUT = 5
