from enum import unique

from cortex_profiles.types.schema import ProfileGroupSchema
from cortex_profiles.utils import EnumWithNamesAsDefaultValue


@unique
class ImplicitAttributeSubjects(EnumWithNamesAsDefaultValue):
    INSIGHT_INTERACTIONS = "insight-interactions"
    APP_USAGE = "application-usage"


@unique
class ImplicitGroupDescriptions(EnumWithNamesAsDefaultValue):
    INFO_CLASSIFICATIONS = "What tags capture of the different classifications of the attributes?"
    DATA_LIMITS = "What tags capture the limits imposed on the data used to generate attributes?"
    SUBJECTS = "What tags represent the coceptual essences of attributes?"
    INTERACTIONS = "What tags capture the different interactions attributes can be optionally related to?"
    APP_ASSOCIATIONS = "What tags capture the different apps attributes can be optionally related to?"
    ALGO_ASSOCIATIONS = "What tags capture the different algos attributes can be optionally related to?"
    CONCEPT_ASSOCIATIONS = "What tags capture the different concepts attributes can be optionally related to?"

@unique
class ImplicitGroups(EnumWithNamesAsDefaultValue):
    INFO_CLASSIFICATIONS = ProfileGroupSchema(id="info-classification", label="IC", description=ImplicitGroupDescriptions.INFO_CLASSIFICATIONS.value)
    DATA_LIMITS = ProfileGroupSchema(id="data-limits", label="DL", description=ImplicitGroupDescriptions.DATA_LIMITS.value)
    SUBJECTS = ProfileGroupSchema(id="subject", label="S", description=ImplicitGroupDescriptions.SUBJECTS.value)
    INTERACTIONS = ProfileGroupSchema(id="interaction", label="I", description=ImplicitGroupDescriptions.INTERACTIONS.value)
    APP_ASSOCIATIONS = ProfileGroupSchema(id="app-association", label="APA", description=ImplicitGroupDescriptions.APP_ASSOCIATIONS.value)
    ALGO_ASSOCIATIONS = ProfileGroupSchema(id="algo-association", label="ALA", description=ImplicitGroupDescriptions.ALGO_ASSOCIATIONS.value)
    CONCEPT_ASSOCIATIONS = ProfileGroupSchema(id="concept-association", label="CA", description=ImplicitGroupDescriptions.CONCEPT_ASSOCIATIONS.value)
