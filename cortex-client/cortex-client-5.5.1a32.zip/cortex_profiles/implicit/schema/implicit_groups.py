from cortex_profiles.types.schema import ProfileGroupSchema
from cortex_profiles.utils import AttrsAsDict


class ImplicitAttributeSubjects(AttrsAsDict):
    INSIGHT_INTERACTIONS = "insight-interactions"
    APP_USAGE = "application-usage"


class ImplicitGroupDescriptions(AttrsAsDict):
    INFO_CLASSIFICATIONS = "What tags capture of the different classifications of the attributes?"
    DATA_LIMITS = "What tags capture the limits imposed on the data used to generate attributes?"
    SUBJECTS = "What tags represent the coceptual essences of attributes?"
    INTERACTION = "What tags capture the different interactions attributes can be optionally related to?"
    APP_ASSOCIATED = "What tags capture the different apps attributes can be optionally related to?"
    ALGO_ASSOCIATED = "What tags capture the different algos attributes can be optionally related to?"
    CONCEPT_ASSOCIATED = "What tags capture the different concepts attributes can be optionally related to?"


class ImplicitGroups(AttrsAsDict):
    INFO_CLASSIFICATIONS = ProfileGroupSchema(
        id="info-classification", label="IC", description=ImplicitGroupDescriptions.INFO_CLASSIFICATIONS)
    DATA_LIMITS = ProfileGroupSchema(
        id="data-limits", label="DL", description=ImplicitGroupDescriptions.DATA_LIMITS)
    SUBJECTS = ProfileGroupSchema(
        id="subject", label="S", description=ImplicitGroupDescriptions.SUBJECTS)
    INTERACTION = ProfileGroupSchema(
        id="interaction", label="I", description=ImplicitGroupDescriptions.INTERACTION)
    APP_ASSOCIATED = ProfileGroupSchema(
        id="app-association", label="APA", description=ImplicitGroupDescriptions.APP_ASSOCIATED)
    ALGO_ASSOCIATED = ProfileGroupSchema(
        id="algo-association", label="ALA", description=ImplicitGroupDescriptions.ALGO_ASSOCIATED)
    CONCEPT_ASSOCIATED = ProfileGroupSchema(
        id="concept-association", label="CA", description=ImplicitGroupDescriptions.CONCEPT_ASSOCIATED)