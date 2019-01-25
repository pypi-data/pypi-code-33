from cortex_profiles.schemas.schemas import DOMAIN_CONCEPTS

INTERACTION_CONFIG = [
    {
        "interaction": "presented",
        "durationOrientedInteraction": False,
        "initiatedByProfile": False,
        "subsetOf": [],
        "mutuallyExlusiveOf": []
    },
    {
        "interaction": "viewed",
        "durationOrientedInteraction": True,
        "initiatedByProfile": True,
        "subsetOf": [("presented", 10, 25)],
        "mutuallyExlusiveOf": ["ignored"]
    },
    {
        "interaction": "ignored",
        "durationOrientedInteraction": False,
        "initiatedByProfile": True,
        "subsetOf": [("presented", 10, 25)],
        "mutuallyExlusiveOf": ["viewed"]
    },
    {
        "interaction": "liked",
        "durationOrientedInteraction": False,
        "initiatedByProfile": True,
        "subsetOf": [("viewed", 10, 50)],
        "mutuallyExlusiveOf": ["disliked"]
    },
    {
        "interaction": "disliked",
        "durationOrientedInteraction": False,
        "initiatedByProfile": True,
        "subsetOf": [("viewed", 10, 35)],
        "mutuallyExlusiveOf": ["liked"]
    }
]

APPS = [ "FNI", "CTI" ]

INSIGHT_TYPES_PER_APP = {
    "CTI": [
        "RetirementInsights",
        "FundOptimizationInsights"
        "InvestmentInsights",
    ],
    "FNI": [
        "FinancialNewsInsights",
        "CompanyMergerInsights",
        "CLevelChangeInsights",
    ]
}

LIMITS_ON_COUNTS_CONCEPTS_OF_TYPE_PER_CONCEPT_SET = {
    DOMAIN_CONCEPTS.PERSON: {"min": 1, "max": 1},
    DOMAIN_CONCEPTS.COMPANY: {"min": 1, "max": 1},
    DOMAIN_CONCEPTS.COUNTRY: {"min": 1, "max": 1},
    DOMAIN_CONCEPTS.CURRENCY: {"min": 1, "max": 1},
    DOMAIN_CONCEPTS.WEBSITE: {"min": 1, "max": 1},
}