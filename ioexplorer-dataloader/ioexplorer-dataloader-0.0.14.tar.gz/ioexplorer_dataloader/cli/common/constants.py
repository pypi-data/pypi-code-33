CONF_PATH = "config.yaml"

DATATYPE_NAMES = [
    "ClinicalSubject",
    "ClinicalSample",
    # 'CNA',
    "Expression",
    "Fusion",
    "SV",
    "TCRSequence",
    "Mutation",
    "Timeline",
]

REQUIRED_DATATYPES = ["ClinicalSubject", "ClinicalSample"]

MODULE_NAMES = ["FilterVariables", "Correlation", "Survival", "Expression"]
