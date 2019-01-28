from typing import List, Optional, Any, Mapping
from faker import Factory, Generator

from cortex_profiles.synthetic.apps import AppProvider, test_app_provider
from cortex_profiles.synthetic.attribute_values import AttributeValueProvider, test_attr_value_provider
from cortex_profiles.synthetic.attributes import AttributeProvider, test_attr_provider
from cortex_profiles.synthetic.concepts import CortexConceptsProvider, test_concept_provider
from cortex_profiles.synthetic.tenant import TenantProvider, test_cortex_provider
from cortex_profiles.synthetic.insights import InsightsProvider, test_insights_provider
from cortex_profiles.synthetic.interactions import InteractionsProvider
from cortex_profiles.synthetic.profiles import ProfileProvider, test_profiles_provider
from cortex_profiles.synthetic.sessions import SessionsProvider, test_sessions_provider
from cortex_profiles.synthetic.schema import SchemaProvider
from cortex_profiles.synthetic.tests import test_insight_distribution, test_insight_interaction_events


def add_provider_with_args(fake:Generator, provider, args):
    initialized_provider = provider(fake, **args)
    fake.add_provider(initialized_provider)
    return fake


def add_provider_with_subset_of_args(fake:Generator, provider, args_to_consider:List[str], all_args:Mapping[str, Any]):
    args = {arg: all_args[arg] for arg in args_to_consider if arg in all_args}
    return add_provider_with_args(fake, provider, args)


# def add_profile_providers(fake:Generator, **kwargs) -> None:
#     """
#     # How do mark the order as mattering with the providers ... or at least that providers depend on each other ...!?
#         # Order doesnt matter, but before a method is called , all dependent providers must be in scope!
#
#     :param fake:
#     :return:
#     """
#
#     # No dependencies
#     fake.add_provider(TenantProvider) # profile_universe, tenant_universe, environment_universe
#     fake.add_provider(CortexConceptsProvider) # concept_universe
#     fake.add_provider(AppProvider) # app_universe
#
#     fake.add_provider(InsightsProvider) # insight_types
#     fake.add_provider(InteractionsProvider) # interactions
#     fake.add_provider(SessionsProvider)
#
#     fake.add_provider(AttributeValueProvider)
#     fake.add_provider(AttributeProvider)
#     fake.add_provider(ProfileProvider)
#
#     return fake


def add_profile_providers(fake:Generator, all_provider_args) -> None:
    """
    # How do mark the order as mattering with the providers ... or at least that providers depend on each other ...!?
        # Order doesnt matter, but before a method is called , all dependent providers must be in scope!

    :param fake:
    :return:
    """

    add_provider_with_subset_of_args(fake, TenantProvider, ["profile_universe", "tenant_universe"], all_provider_args)
    add_provider_with_subset_of_args(fake, CortexConceptsProvider, ["concept_universe"], all_provider_args)
    add_provider_with_subset_of_args(fake, AppProvider, ["app_universe"], all_provider_args)
    add_provider_with_subset_of_args(fake, InsightsProvider, ["insight_types", "concept_limits_per_insight"], all_provider_args)
    add_provider_with_subset_of_args(fake, InteractionsProvider, ["interactions"], all_provider_args)

    fake.add_provider(SessionsProvider)
    fake.add_provider(AttributeValueProvider)
    fake.add_provider(AttributeProvider)
    fake.add_provider(ProfileProvider)
    fake.add_provider(SchemaProvider)

    return fake


def create_profile_synthesizer(**kwargs):
    profile_synthesizer = Factory.create()
    profile_synthesizer = add_profile_providers(profile_synthesizer, kwargs)
    return profile_synthesizer


def test(f):
    test_app_provider(f)
    test_attr_value_provider(f)
    test_attr_provider(f)
    test_concept_provider(f)
    test_cortex_provider(f)
    test_insights_provider(f)
    test_insight_distribution(f)
    test_insight_interaction_events(f)
    test_profiles_provider(f)
    test_sessions_provider(f)


# TODO ... make insights.tags get a set of concepts ...
# TODO ... make concept_limits_on_insights work ...

if __name__ == "__main__":
    # test(create_profile_synthesizer())
    test(create_profile_synthesizer(
        profile_universe=[str(x) for x in range(0, 9)],
        tenant_universe=["cortex-accelerators"],
        concept_universe=[
            {
                "context": "cortex/person",
                "id": "Bill Gates",
                "title": "cortex/person"
            },
            {
                "context": "cortex/company",
                "id": "Apple Inc",
                "title": "cortex/company"
            }
        ],
        concept_limits_per_insight={
            "cortex/person": {
                "min": 1,
                "max": 3
            },
            "cortex/company": {
                "min": 1,
                "max": 1
            }
        },
        app_universe=["FNI"],
        insight_types={
            "FNI": [
                "offer-insights"
            ]
        },
        interactions=[
            {
                "interaction": "presented",
                "durationOrientedInteraction": False,
                "subsetOf": [],
                "mutuallyExlusiveOf": []
            },
            {
                "interaction": "viewed",
                "durationOrientedInteraction": True,
                "subsetOf": [("presented", 10, 25)],
                "mutuallyExlusiveOf": []
            },
            {
                "interaction": "liked",
                "durationOrientedInteraction": False,
                "subsetOf": [("viewed", 10, 50)],
                "mutuallyExlusiveOf": ["disliked"]
            },
            {
                "interaction": "disliked",
                "durationOrientedInteraction": False,
                "subsetOf": [("viewed", 10, 35)],
                "mutuallyExlusiveOf": ["liked"]
            }
        ]
    ))
