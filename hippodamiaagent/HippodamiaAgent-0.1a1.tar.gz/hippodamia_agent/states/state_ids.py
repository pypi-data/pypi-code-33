from enum import Enum


class state_ids(Enum):
    Uninitialized = 1
    Initialized = 2
    Onboarding = 3
    Onboarded = 4
    Active = 5
    Terminating = 6
