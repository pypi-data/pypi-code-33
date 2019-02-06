import itertools
from typing import Set, List, Mapping, Optional, Tuple

from iso3166 import countries as countries

from cortex_profiles.schemas.schemas import DOMAIN_CONCEPTS
from cortex_profiles.synthetic import defaults
from cortex_profiles.synthetic.base import BaseProviderWithDependencies
from cortex_profiles.types.insights import Link
from cortex_profiles.utils import get_unique_cortex_objects
from cortex_profiles.utils import group_by_key, flatten_list_recursively


LIMITS_ON_COUNTS_CONCEPTS_OF_TYPE_WITHIN_UNIVERSE = {
    DOMAIN_CONCEPTS.PERSON: 50,
    DOMAIN_CONCEPTS.COMPANY: 50,
    DOMAIN_CONCEPTS.COUNTRY: 50,
    DOMAIN_CONCEPTS.CURRENCY: 50,
    DOMAIN_CONCEPTS.WEBSITE: 50
}

# TODO ... for the attribute building to work right ... the title needs to be the context of the tag ... not the name ...

def get_person(fake) -> dict:
    return {
        "id": "{} {}".format(fake.first_name(), fake.last_name()),
        "context": DOMAIN_CONCEPTS.PERSON,
        "title": DOMAIN_CONCEPTS.PERSON,
    }


def get_company(fake) -> dict:
    return {
        "id": fake.company(),
        "context": DOMAIN_CONCEPTS.COMPANY,
        "title": DOMAIN_CONCEPTS.COMPANY,
    }


def get_country(fake) -> dict:
    country = countries.get(fake.country_code(representation='alpha-3'))
    return {
        "id": "{}({})".format(country.alpha3, country.name),
        "context": DOMAIN_CONCEPTS.COUNTRY,
        "title": DOMAIN_CONCEPTS.COUNTRY
    }


def get_currency(fake) -> dict:
    currency = fake.currency()
    return {
        "id": "{}({})".format(currency[0], currency[1]),
        "context": DOMAIN_CONCEPTS.CURRENCY,
        "title": DOMAIN_CONCEPTS.CURRENCY,
    }


def get_website(fake) -> dict:
    return {
        "id": "{0}".format(fake.url()),
        "context": DOMAIN_CONCEPTS.WEBSITE,
        "title": DOMAIN_CONCEPTS.WEBSITE
    }


class CortexConceptsProvider(BaseProviderWithDependencies):

    def __init__(self, *args, concept_universe:List[dict]=None, concept_limits=LIMITS_ON_COUNTS_CONCEPTS_OF_TYPE_WITHIN_UNIVERSE, **kwargs):
        super(CortexConceptsProvider, self).__init__(*args, **kwargs)
        self.concepts_to_choose_from:List[Link] = concept_universe if concept_universe else self.universe_of_concepts(concept_limits)
        self.indexed_concepts_to_choose_from = group_by_key(self.concepts_to_choose_from, lambda x: x["context"])

    def dependencies(self) -> List[type]:
        return []

    def universe_of_concepts(self, limits) -> List[dict]:
        """
        This creates a universe of concepts indexed by the concept type where concepts are unique.
        :return:
        """
        concepts = [
            get_unique_cortex_objects(lambda: get_person(self.fake), limits[DOMAIN_CONCEPTS.PERSON]),
            get_unique_cortex_objects(lambda: get_company(self.fake), limits[DOMAIN_CONCEPTS.COMPANY]),
            get_unique_cortex_objects(lambda: get_country(self.fake), limits[DOMAIN_CONCEPTS.COUNTRY]),
            get_unique_cortex_objects(lambda: get_currency(self.fake), limits[DOMAIN_CONCEPTS.CURRENCY]),
            get_unique_cortex_objects(lambda: get_website(self.fake), limits[DOMAIN_CONCEPTS.WEBSITE])
        ]
        return flatten_list_recursively(concepts)

    def set_of_concepts(self, concept_limits:Mapping[str,Tuple[int]]) -> Set[Link]:
        """
        Its more likely that concept limits will be a default dict ... with like 1 ...
        Its more likely the universe will be a list of all the different options ...
        :param concept_limits:
        :return:
        """

        all_concepts = set(list(self.indexed_concepts_to_choose_from) + list(concept_limits))

        min_number_of_choosable_concepts_per_type = {
            concept_type: min(concept_limits.get(concept_type, (0,None))[0], len(self.indexed_concepts_to_choose_from.get(concept_type, [])))
            for concept_type in all_concepts
        }
        max_number_of_choosable_concepts_per_type = {
            concept_type: min(concept_limits.get(concept_type, (None,0))[1], len(self.indexed_concepts_to_choose_from.get(concept_type, [])))
            for concept_type in all_concepts
        }
        number_of_concepts_chosen_per_type = {
            concept_type: self.fake.random.randint(
                min_number_of_choosable_concepts_per_type[concept_type],
                max_number_of_choosable_concepts_per_type[concept_type]
            )
            for concept_type in all_concepts
        }
        concept_choices = [
            list(self.fake.random.choice(list(
                itertools.combinations(
                    concepts,
                    number_of_concepts_chosen_per_type[concept_type]
                )
            )))
            for concept_type, concepts in self.indexed_concepts_to_choose_from.items()
        ]
        return flatten_list_recursively(concept_choices, remove_empty_lists=True)

    def _concept(self, context) -> Optional[Link]:
        concept = self.fake.random.choice(self.indexed_concepts_to_choose_from.get(context)) if context in self.indexed_concepts_to_choose_from else None
        return Link(**concept) if concept else None

    def cortex_person(self) -> Optional[Link]:
        return self._concept(DOMAIN_CONCEPTS.PERSON)

    def cortex_company(self) -> Optional[Link]:
        return self._concept(DOMAIN_CONCEPTS.COMPANY)

    def cortex_country(self) -> Optional[Link]:
        return self._concept(DOMAIN_CONCEPTS.COUNTRY)

    def cortex_currency(self) -> Optional[Link]:
        return self._concept(DOMAIN_CONCEPTS.CURRENCY)

    def cortex_website(self) -> Optional[Link]:
        return self._concept(DOMAIN_CONCEPTS.WEBSITE)

    def concept(self) -> Link:
        returnVal = None
        while returnVal is None:
            random_category = self.fake.random.choice(list(self.indexed_concepts_to_choose_from))
            returnVal = self._concept(random_category)
        return returnVal


def test_concept_provider(f):
    from cortex_profiles.utils import json_makeup
    # print(json_makeup(f.universe_of_concepts(LIMITS_ON_COUNTS_CONCEPTS_OF_TYPE_WITHIN_UNIVERSE)))
    for x in range(0, 5):
        print(json_makeup(f.set_of_concepts(defaults.LIMITS_ON_COUNTS_CONCEPTS_OF_TYPE_PER_CONCEPT_SET)))
    # for x in range(0, 100):
    #     print(f.concept())


if __name__ == "__main__":
    from cortex_profiles.synthetic import create_profile_synthesizer
    f = create_profile_synthesizer()

    test_concept_provider(f)

    f = CortexConceptsProvider(f, concept_universe=[
        {
            "context": "cortex/person",
            "id": "Richard Santiago",
            "title": "cortex/person"
        }
    ])

    test_concept_provider(f)

    for x in range(0,10):
        print(f.concept())
