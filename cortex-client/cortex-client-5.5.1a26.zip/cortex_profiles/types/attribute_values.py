import json
from typing import Any, List, Union, Callable

import numpy as np
import pydash
from attr import attrs, fields
from cortex_profiles.schemas.schemas import CONTEXTS, VERSION
from cortex_profiles.types.schema import ProfileValueTypeSummary
from cortex_profiles.types.utils import describableAttrib, CONTEXT_DESCRIPTION, VERSION_DESCRIPTION, \
    ATTRIBUTE_SUMMARY_DESCRIPTION
from cortex_profiles.types.utils import str_or_context
from cortex_profiles.utils import converter_for_list_of_classes, converter_for_union_type, union_type_validator


# Bool is getting consumes by the union since it is a subclass of int ...

PrimitiveJSONTypes = (str, int, float, bool, type(None))
PrimitiveJSONUnionType = Union[PrimitiveJSONTypes]
PrimitiveJSONTypeHandlers = pydash.merge(dict(zip(PrimitiveJSONTypes[:-1], PrimitiveJSONTypes[:-1])), {type(None): lambda x: None})

ObjectJSONTypes = (dict, type(None))
ObjectJSONUnionType = Union[ObjectJSONTypes]
ObjectJSONTypeHandlers = pydash.merge(dict(zip(ObjectJSONTypes[:-1], ObjectJSONTypes[:-1])), {type(None): lambda x: None})

ListJSONTypes = (list, type(None))
ListJSONUnionType = Union[ListJSONTypes]
ListJSONTypeHandlers = pydash.merge(dict(zip(ListJSONTypes[:-1], ListJSONTypes[:-1])), {type(None): lambda x: None})

JSONUnionTypes = Union[str, int, float, bool, type(None), dict, list]


@attrs(frozen=True)
class BaseAttributeValue(object):
    """
    Interface Attribute Values Need to Adhere to ...
    """
    value = describableAttrib(type=object, description="What value is captured in the attribute?")
    context = describableAttrib(type=str, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @classmethod
    def detailed_schema_type(cls) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(
            outerType=fields(cls).context.default,
            innerTypes=[]
        )


# - [ ] Do we put versions on everything ... even it its meant to be nested? or only stuff saved in db?
@attrs(frozen=True)
class Dimension(object):
    """
    Representing a single dimension in a dimensional attribute ...
    """
    dimensionId = describableAttrib(type=str, description="What entity does this dimension represent?")
    dimensionValue = describableAttrib(type=Union[str, list, dict, int, bool, float], description="What is the value of this dimension?")


@attrs(frozen=True)
class PrimitiveValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary JSON Object / Map / Hash as their value
    """
    value = describableAttrib(
        type=PrimitiveJSONUnionType,
        validator=union_type_validator(PrimitiveJSONUnionType),
        converter=converter_for_union_type(PrimitiveJSONUnionType, PrimitiveJSONTypeHandlers),
        description="What is the value of the object itself?")
    context = describableAttrib(type=str, default=CONTEXTS.PRIMITIVE_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return json.dumps(self.value)


@attrs(frozen=True)
class ObjectValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary JSON Object / Map / Hash as their value
    """
    value = describableAttrib(
        type=ObjectJSONUnionType,
        validator=union_type_validator(ObjectJSONUnionType),
        factory=dict,
        converter=converter_for_union_type(ObjectJSONUnionType, ObjectJSONTypeHandlers),
        description="What is the value of the object itself?")
    context = describableAttrib(type=str, default=CONTEXTS.OBJECT_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return json.dumps(self.value)


@attrs(frozen=True)
class ListValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary JSON List / Array as their value.
    """
    value = describableAttrib(
        type=ListJSONUnionType,
        validator=union_type_validator(ListJSONUnionType),
        factory=list,
        converter=converter_for_union_type(ListJSONUnionType, ListJSONTypeHandlers),
        description="What is the value of the object itself?")
    context = describableAttrib(type=str, default=CONTEXTS.LIST_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        if self.value is None:
            return None
        value = self.value if isinstance(self.value, list) else list(self.value)
        return json.dumps(self.value)

    @classmethod
    def detailed_schema_type(cls, typeOfItems:Union[str,type]) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(
            outerType = fields(cls).context.default,
            innerTypes = [
                ProfileValueTypeSummary(outerType=str_or_context(typeOfItems))
            ]
        )



@attrs(frozen=True)
class RelationshipValue(BaseAttributeValue):
    """
    Representing the content of a percentage attribute ...
    """
    value = describableAttrib(type=str, description="What is the id of the related concept to the profile?")
    relatedConceptType = describableAttrib(type=str, description="What is the type of the related concept?")
    relationshipType = describableAttrib(type=str, description="How is the related concept related to the profile? What is the type of relationship?")
    relationshipTitle = describableAttrib(type=str, description="What is a short, human readable description of the relationship between the profile and the related concept?")
    relatedConceptTitle = describableAttrib(type=str, description="What is a short, human readable description of the related concept to the profile?")
    relationshipProperties = describableAttrib(type=dict, default={}, description="What else do we need to know about the relationship?")
    context = describableAttrib(type=str, default=CONTEXTS.RELATIONSHIP_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return "Profile-{}->{}".format(self.relationshipTitle, self.relatedConceptTitle)


@attrs(frozen=True)
class NumericAttributeValue(BaseAttributeValue):
    """
    Representing the content of a numeric attribute ...
    """
    value = describableAttrib(type=Union[int, float], description="What is the number that we are interested in?")
    context = describableAttrib(type=str, default=CONTEXTS.NUMERICAL_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return "{:.3f}".format(self.value)


@attrs(frozen=True)
class NumericWithUnitValue(NumericAttributeValue):
    """
    Representing the content of a numeric attribute as a measuring unit ...
    """
    value = describableAttrib(type=Union[int, float], default=0, description="What numeric value is captured by this attribute value?")
    unitId = describableAttrib(type=str, default=None, description="What is the unique id of the unit? i.e USD, GBP, %, ...")
    unitContext = describableAttrib(type=str, default=None, description="What type of unit is this? i.e currency, population of country, ...")
    unitTitle = describableAttrib(type=str, default=None, description="What is the symbol desired to represent the unit?")
    unitIsPrefix = describableAttrib(type=bool, default=False, description="Should the symbol be before or after the unit?")


@attrs(frozen=True)
class PercentileAttributeValue(NumericAttributeValue):
    """
    Representing the content of a percentile attribute ...
    """
    value = describableAttrib(type=float, description="What is the numeric value of the percentile?")
    context = describableAttrib(type=str, default=CONTEXTS.PERCENTILE_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return "{:.3f}%%".format(self.value)


@attrs(frozen=True)
class PercentageAttributeValue(NumericAttributeValue):
    """
    Representing the content of a percentage attribute ...
    """
    value = describableAttrib(type=float, description="What numeric value of the percentage?")
    context = describableAttrib(type=str, default=CONTEXTS.PERCENTAGE_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
    @summary.default
    def summarize(self):
        return "{:.2f}%".format(self.value)


@attrs(frozen=True)
class AverageAttributeValue(NumericAttributeValue):
    """
    Representing the content of a percentage attribute ...
    """
    value = describableAttrib(type=float, description="What numeric value of the average?")
    context = describableAttrib(type=str, default=CONTEXTS.AVERAGE_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
    @summary.default
    def summarize(self):
        return "Avg: {:.3f}".format(self.value)


@attrs(frozen=True)
class CounterAttributeContent(NumericWithUnitValue):
    """
    Representing the content of a counter attribute ...
    """
    value = describableAttrib(type=int, default=0, description="What is the numeric value of the current total?")
    context = describableAttrib(type=str, default=CONTEXTS.COUNTER_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
    @summary.default
    def summarize(self):
        return "{}{}{}".format(
            ("{} ".format(self.unitTitle) if (self.unitIsPrefix and self.unitTitle) else ""),
            ("{}".format(self.value)),
            (" {}".format(self.unitTitle) if (self.unitTitle and not self.unitIsPrefix) else "")
        )


@attrs(frozen=True)
class TotalAttributeContent(NumericWithUnitValue):
    """
    Representing the content of a total attribute ...
    """
    value = describableAttrib(type=float, default=0.0, description="What is the current total?")
    context = describableAttrib(type=str, default=CONTEXTS.TOTAL_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
    @summary.default
    def summarize(self):
        return "{}{}{}".format(
            ("{} ".format(self.unitTitle) if (self.unitIsPrefix and self.unitTitle) else ""),
            ("{:.3f}".format(self.value)),
            (" {}".format(self.unitTitle) if (self.unitTitle and not self.unitIsPrefix) else "")
        )


@attrs(frozen=True)
class ConceptValue(BaseAttributeValue):
    """
    Representing a concept ...
    """
    value = describableAttrib(type=str, description="What is the name of the concept?")
    context = describableAttrib(type=str, default=CONTEXTS.CONCEPT_ATTRIBUTE_VALUE, description="What is the type of this piece of data?")
    version = describableAttrib(type=str, default=VERSION, description="What version is the schema of this piece of data based on?")
    summary = describableAttrib(type=str, description="How can this piece of data be best summarized?")

    @summary.default
    def summarize(self):
        return self.value


@attrs(frozen=True)
class DimensionalAttributeContent(BaseAttributeValue):
    """
    Representing the content of a 2-dimensional attribute.
    """

    value = describableAttrib(
        type=List[Dimension],
        converter=lambda x: converter_for_list_of_classes(x, Dimension),
        description="What are the different dimensions captured in the attribute value?"
    )
    contextOfDimension = describableAttrib(type=str, description="What type are the dimensions?")
    contextOfDimensionValue = describableAttrib(type=str, description="What type are the values associated with the dimension?")
    context = describableAttrib(type=str, default=CONTEXTS.DIMENSIONAL_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        average = None
        max = None
        min = None
        # TODO ... right now the value ... is just a value ... not an NumericAttributeValue ...
        # if all(map(lambda x: isinstance(x.dimensionValue, NumericAttributeValue), self.value)):
        #     average = np.mean(list(map(lambda x: x.dimensionValue.value, self.value)))
        #     max = np.max(list(map(lambda x: x.dimensionValue.value, self.value)))
        #     min = np.min(list(map(lambda x: x.dimensionValue.value, self.value)))
        # print(list(map(lambda x: x.dimensionValue, self.value)))
        # print(list(map(lambda x: isinstance(x.dimensionValue, (int, float)), self.value)))
        if all(map(lambda x: isinstance(x.dimensionValue, (int, float)), self.value)):
            average = np.mean(list(map(lambda x: x.dimensionValue, self.value)))
            max = np.max(list(map(lambda x: x.dimensionValue, self.value)))
            min = np.min(list(map(lambda x: x.dimensionValue, self.value)))
        return "{}{}{}{}".format(
            ("Dimensions: {}".format(len(self.value))),
            (", Avg: {:.3f}".format(average) if average else ""),
            (", Min: {:.3f}".format(average) if min else ""),
            (", Max: {:.3f}".format(average) if max else "")
        )

    @classmethod
    def detailed_schema_type(cls, firstDimensionType:Union[str,type], secondDimensionType:Union[str,type]) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(
            outerType = fields(cls).context.default,
            innerTypes = [
                ProfileValueTypeSummary(outerType=str_or_context(firstDimensionType)),
                ProfileValueTypeSummary(outerType=str_or_context(secondDimensionType))
            ]
        )

# class PlacementAttributeContent 1st, 2nd, 3rd ...
# class {Rank/Score}AttributeContent

# TODO : Rename the attribute values ... some are AttributeContent and Some are AttributeVlaue ...


def load_profile_attribute_value_from_dict(d:dict) -> BaseAttributeValue:
    if d.get("context") == CONTEXTS.OBJECT_PROFILE_ATTRIBUTE_VALUE:
        return ObjectValue(**d)
    if d.get("context") == CONTEXTS.RELATIONSHIP_PROFILE_ATTRIBUTE_VALUE:
        return RelationshipValue(**d)
    if d.get("context") == CONTEXTS.PERCENTILE_PROFILE_ATTRIBUTE_VALUE:
        return PercentileAttributeValue(**d)
    if d.get("context") == CONTEXTS.PERCENTAGE_PROFILE_ATTRIBUTE_VALUE:
        return PercentageAttributeValue(**d)
    if d.get("context") == CONTEXTS.AVERAGE_PROFILE_ATTRIBUTE_VALUE:
        return AverageAttributeValue(**d)
    if d.get("context") == CONTEXTS.COUNTER_PROFILE_ATTRIBUTE_VALUE:
        return CounterAttributeContent(**d)
    if d.get("context") == CONTEXTS.TOTAL_PROFILE_ATTRIBUTE_VALUE:
        return TotalAttributeContent(**d)
    if d.get("context") == CONTEXTS.DIMENSIONAL_PROFILE_ATTRIBUTE_VALUE:
        return DimensionalAttributeContent(**d)
    if d.get("context") == CONTEXTS.NUMERICAL_PROFILE_ATTRIBUTE_VALUE:
        return NumericAttributeValue(**d)
    if d.get("context") == CONTEXTS.PRIMITIVE_PROFILE_ATTRIBUTE_VALUE:
        return PrimitiveValue(**d)
    if d.get("context") == CONTEXTS.LIST_PROFILE_ATTRIBUTE_VALUE:
        return ListValue(**d)
