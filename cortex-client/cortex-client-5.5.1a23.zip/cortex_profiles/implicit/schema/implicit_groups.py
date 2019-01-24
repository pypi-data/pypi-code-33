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
    INTERACTION = "What tags capture the different interactions attributes can be optionally related to?"
    APP_ASSOCIATED = "What tags capture the different apps attributes can be optionally related to?"
    ALGO_ASSOCIATED = "What tags capture the different algos attributes can be optionally related to?"
    CONCEPT_ASSOCIATED = "What tags capture the different concepts attributes can be optionally related to?"

@unique
class ImplicitGroups(EnumWithNamesAsDefaultValue):
    INFO_CLASSIFICATIONS = ProfileGroupSchema(id="info-classification", label="IC", description=ImplicitGroupDescriptions.INFO_CLASSIFICATIONS.value)
    DATA_LIMITS = ProfileGroupSchema(id="data-limits", label="DL", description=ImplicitGroupDescriptions.DATA_LIMITS.value)
    SUBJECTS = ProfileGroupSchema(id="subject", label="S", description=ImplicitGroupDescriptions.SUBJECTS.value)
    INTERACTION = ProfileGroupSchema(id="interaction", label="I", description=ImplicitGroupDescriptions.INTERACTION.value)
    APP_ASSOCIATED = ProfileGroupSchema(id="app-association", label="APA", description=ImplicitGroupDescriptions.APP_ASSOCIATED.value)
    ALGO_ASSOCIATED = ProfileGroupSchema(id="algo-association", label="ALA", description=ImplicitGroupDescriptions.ALGO_ASSOCIATED.value)
    CONCEPT_ASSOCIATED = ProfileGroupSchema(id="concept-association", label="CA", description=ImplicitGroupDescriptions.CONCEPT_ASSOCIATED.value)