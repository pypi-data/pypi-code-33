from cortex_profiles.utils import AttrsAsDict


VERSION = "0.0.1"


class CONTEXTS(AttrsAsDict):
    SESSION="cortex/session"
    INSIGHT="cortex/insight"
    INSIGHT_CONCEPT_TAG="cortex/insight-concept-tag"
    INSIGHT_TAG_RELATIONSHIP="cortex/insight-concept-relationship"
    INSIGHT_TAG_RELATED_TO_RELATIONSHIP="cortex/insight-relatedTo-concept"
    INSIGHT_INTERACTION="cortex/insight-interaction"
    PROFILE_SNAPSHOT="cortex/profile-snapshot"
    PROFILE="cortex/profile"
    PROFILE_COMMIT="cortex/profile-commit"
    PROFILE_SCHEMA="cortex/profile-schema"
    PROFILE_ATTRIBUTE_TAG="cortex/profile-attribute-tag"
    PROFILE_ATTRIBUTE_GROUP="cortex/profile-attribute-group"
    DECLARED_PROFILE_ATTRIBUTE="cortex/attributes-declared"
    OBSERVED_PROFILE_ATTRIBUTE="cortex/attributes-observed"
    INFERRED_PROFILE_ATTRIBUTE="cortex/attributes-inferred"
    ASSIGNED_PROFILE_ATTRIBUTE = "cortex/attributes-assigned"
    END_USER_PROFILE="cortex/profile-of-end-user"
    RELATIONSHIP_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-relationship"
    OBJECT_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-object"
    LIST_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-list"
    PRIMITIVE_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-primitive"
    NUMERICAL_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-numerical"
    PERCENTILE_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-percentile"
    PERCENTAGE_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-percentage"
    AVERAGE_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-average"
    TOTAL_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-total"
    COUNTER_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-counter"
    CLASSIFICATION_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-classification"
    DIMENSIONAL_PROFILE_ATTRIBUTE_VALUE="cortex/attribute-value-dimensional"
    CONCEPT_ATTRIBUTE_VALUE="cortex/attribute-value-concept"
    DAY="cortex/time-day"


class UNIVERSAL_ATTRIBUTES(AttrsAsDict):
    TYPES = "profile.types"

    @staticmethod
    def keys():
        return list(filter(lambda x: x[0] != "_", CONTEXTS.__dict__.keys()))


class DOMAIN_CONCEPTS(AttrsAsDict):
    PERSON="cortex/person"
    COUNTRY="cortex/country"
    CURRENCY="cortex/currency"
    COMPANY="cortex/company"
    WEBSITE="cortex/website"


class INTERACTIONS(AttrsAsDict):
    CONTEXT=CONTEXTS.INSIGHT_INTERACTION
    PRESENTED="presented"
    VIEWED="viewed"
    IGNORED="ignored"


# class TraderProfileAttributes(AttrsAsDict):
#     INSIGHTS_PRESENTED_PER_INSIGHTT_TYPE="insights.presented.perInsightType.total"
#     INSIGHTS_VIEWED_PER_INSIGHTT_TYPE="insights.viewed.perInsightType.total"
#     INSIGHTS_IGNORED_PER_INSIGHTT_TYPE="insights.ignored.perInsightType.total"
#     INSIGHTS_PRESENTED_RECENTLY_PER_INSIGHTT_TYPE="insights.recentlyPresented.perInsightType.total"
#     INSIGHTS_VIEWED_RECENTLY_PER_INSIGHTT_TYPE="insights.recentlyViewed.perInsightType.total"
#     INSIGHTS_IGNORED_RECENTLY_PER_INSIGHTT_TYPE="insights.recentlyIgnored.perInsightType.total"
#     INSIGHTS_PRESENTED_RELATED_TO_COMPANIES="insights.presented.relatedToCompanies.total"
#     INSIGHTS_PRESENTED_RELATED_TO_SECTORS="insights.presented.relatedToSectors.total"
#     INSIGHTS_PRESENTED_RELATED_TO_MARKET_INDICES="insights.presented.relatedToMarketIndices.total"
#     INSIGHTS_PRESENTED_RELATED_TO_COUNTRIES="insights.presented.relatedToCountriesOfExchanges.total"
#     INSIGHTS_PRESENTED_RECENTLY_RELATED_TO_COMPANIES="insights.recentlyPresented.relatedToCompanies.total"
#     INSIGHTS_PRESENTED_RECENTLY_RELATED_TO_SECTORS="insights.recentlyPresented.relatedToSectors.total"
#     INSIGHTS_PRESENTED_RECENTLY_RELATED_TO_MARKET_INDICES="insights.recentlyPresented.relatedToMarketIndices.total"
#     INSIGHTS_PRESENTED_RECENTLY_RELATED_TO_COUNTRIES="insights.recentlyPresented.relatedToCountriesOfExchanges.total"
#     INSIGHTS_VIEWED_RELATED_TO_COMPANIES="insights.viewed.relatedToCompanies.total"
#     INSIGHTS_VIEWED_RELATED_TO_SECTORS="insights.viewed.relatedToSectors.total"
#     INSIGHTS_VIEWED_RELATED_TO_MARKET_INDICES="insights.viewed.relatedToMarketIndices.total"
#     INSIGHTS_VIEWED_RELATED_TO_COUNTRIES="insights.viewed.relatedToCountriesOfExchanges.total"
#     INSIGHTS_VIEWED_RECENTLY_RELATED_TO_COMPANIES="insights.recentlyViewed.relatedToCompanies.total"
#     INSIGHTS_VIEWED_RECENTLY_RELATED_TO_SECTORS="insights.recentlyViewed.relatedToSectors.total"
#     INSIGHTS_VIEWED_RECENTLY_RELATED_TO_MARKET_INDICES="insights.recentlyViewed.relatedToMarketIndices.total"
#     INSIGHTS_VIEWED_RECENTLY_RELATED_TO_COUNTRIES="insights.recentlyViewed.relatedToCountriesOfExchanges.total"
#     INSIGHTS_IGNORED_RELATED_TO_COMPANIES="insights.ignored.relatedToCompanies.total"
#     INSIGHTS_IGNORED_RELATED_TO_SECTORS="insights.ignored.relatedToSectors.total"
#     INSIGHTS_IGNORED_RELATED_TO_MARKET_INDICES="insights.ignored.relatedToMarketIndices.total"
#     INSIGHTS_IGNORED_RELATED_TO_COUNTRIES="insights.ignored.relatedToCountriesOfExchanges.total"
#     INSIGHTS_IGNORED_RECENTLY_RELATED_TO_COMPANIES="insights.recentlyIgnored.relatedToCompanies.total"
#     INSIGHTS_IGNORED_RECENTLY_RELATED_TO_SECTORS="insights.recentlyIgnored.relatedToSectors.total"
#     INSIGHTS_IGNORED_RECENTLY_RELATED_TO_MARKET_INDICES="insights.recentlyIgnored.relatedToMarketIndices.total"
#     INSIGHTS_IGNORED_RECENTLY_RELATED_TO_COUNTRIES="insights.recentlyIgnored.relatedToCountriesOfExchanges.total"
#     TIME_SPENT_ON_INSIGHTS_RELATED_TO_COMPANIES="insights.duration.relatedToCompanies.total"
#     TIME_SPENT_ON_INSIGHTS_RELATED_TO_SECTORS="insights.duration.relatedToSectors.total"
#     TIME_SPENT_ON_INSIGHTS_RELATED_TO_MARKET_INDICES="insights.duration.relatedToMarketIndices.total"
#     TIME_SPENT_ON_INSIGHTS_RELATED_TO_COUNTRIES="insights.duration.relatedToCountriesOfExchanges.total"
#     LOGINS_DURATION_TOTAL="logins.duration.appSpecific.total"
#     LOGINS_RECENT_DURATION_TOTAL="logins.recentDuration.appSpecific.total"
#     LOGINS_DAILY_DURATION_TOTAL="logins.dailyDuration.appSpecific.total"
#     LOGINS_RECENT_DAILY_DURATION_TOTAL="logins.recentDailyDuration.appSpecific.total"
#     LOGINS_DAILY_DURATION_AVERAGE="logins.dailyDuration.appSpecific.average"
#     LOGINS_RECENT_DAILY_DURATION_AVERAGE="logins.recentDailyDuration.appSpecific.average"
#     LOGINS_TOTAL="logins.instances.appSpecific.total"
#     LOGINS_RECENT_TOTAL="logins.recentInstances.appSpecific.total"
#     LOGINS_DAILY_TOTALS="logins.dailyInstances.appSpecific.total"
#     LOGINS_RECENT_DAILY_TOTALS="logins.recentDailyInstances.appSpecific.total"
#     LOGINS_DAILY_AVERAGE="logins.dailyInstances.appSpecific.average"
#     LOGINS_RECENT_DAILY_AVERAGE="logins.recentDailyInstances.appSpecific.average"
