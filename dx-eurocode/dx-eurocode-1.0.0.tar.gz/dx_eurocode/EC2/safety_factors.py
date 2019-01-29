"""Safety factors defined in EC2."""
from ..EC0.safety_factors import BaseSafetyFactor


#: Safety factor for concrete
CONCRETE_SAFETY_FACTOR = BaseSafetyFactor(
    values={
        'persistent':{
            'ultimate': 1.5,
            },
        'transient':{
            'ultimate': 1.5,
            },
        'accidental':{
            'ultimate': 1.2,
            },
        }
    )


#: Safety factor for steel
STEEL_SAFETY_FACTOR = BaseSafetyFactor(
    values={
        'persistent':{
            'ultimate': 1.15,
            },
        'transient':{
            'ultimate': 1.15,
            },
        'accidental':{
            'ultimate': 1.0,
            },
        }
    )

#: Safety factor for steel used in pretension
STEEL_PRETENSION_SAFETY_FACTOR = BaseSafetyFactor(
    values={
        'persistent':{
            'ultimate': 1.15,
            },
        'transient':{
            'ultimate': 1.15,
            },
        'accidental':{
            'ultimate': 1.0,
            },
        }
    )
