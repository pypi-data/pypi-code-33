from enum import Enum


class event_ids(Enum):
    sigint = 1
    new_uuid = 2
    timeout = 3
    onboarding_request = 4
    onboarding_response = 5
    reonboarding_request = 6
    termination = 7
    activate = 8
