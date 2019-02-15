# -*- coding: utf-8 -*-


import logging
import os
import pkg_resources


from openfisca_ceq import (
    CountryTaxBenefitSystem as CEQTaxBenefitSystem,
    entities,
    )

log = logging.getLogger(__name__)


ceq_variables_directory = os.path.join(
    pkg_resources.get_distribution('openfisca-ceq').location,
    'openfisca_ceq',
    'variables'
    )

assert os.path.exists(ceq_variables_directory)

ceq_input_variables = {
    name
    for name, variable in CEQTaxBenefitSystem().variables.items()
    if len(variable.formulas) == 0
    }

ceq_computed_variables = {
    name
    for name, variable in CEQTaxBenefitSystem().variables.items()
    if len(variable.formulas) > 0
    }


def add_ceq_framework(country_tax_benefit_system):
    country_entities = country_tax_benefit_system.entities
    entities_by_name = dict((entity.key, entity) for entity in country_entities)
    entities.Person = entities_by_name['person']
    entities.Household = entities_by_name['household']
    country_variables = set(country_tax_benefit_system.variables.keys())

    input_intersection_country = ceq_input_variables.intersection(country_variables)
    if input_intersection_country:
        log.info("Country variables replacing CEQ input variables:\n{}".format(
            " - " + ('\n - ').join(
                list(sorted(input_intersection_country))
                )
            ))
    input_difference_country = ceq_input_variables.difference(country_variables)
    if input_difference_country:
        log.info("Missing CEQ input variables:\n{}".format(
            " - " + ('\n - ').join(
                list(sorted(input_difference_country))
                )
            ))
    computed_intersection_country = ceq_computed_variables.intersection(country_variables)
    if computed_intersection_country:
        log.info("Country variables replacing CEQ computed variables:\n{}".format(
            " - " + ('\n - ').join(
                list(sorted(computed_intersection_country))
                )
            ))

    ignored_variables = country_variables
    assert not country_variables.intersection(ceq_computed_variables), \
        "Some country variables matches computed CEQ variables: {}".format(
            country_variables.intersection(ceq_computed_variables))

    country_tax_benefit_system.add_variables_from_directory(ceq_variables_directory,
        ignored_variables = ignored_variables)

    return country_tax_benefit_system
