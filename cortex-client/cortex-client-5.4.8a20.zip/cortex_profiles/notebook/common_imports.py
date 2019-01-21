import copy
from collections import Counter

import arrow
import attr
import numpy as np
import pandas as pd
from cortex_client.profilesclient import ProfilesClient
from cortex_profiles.visualize import ProfileVisualizationClient
from cortex_profiles import implicit_attribute_builders, \
    implicit_attribute_builder_utils, implicit_insight_attribute_builders, \
    implicit_login_attribute_builders
from cortex_profiles import utils, utils_for_dfs, profile_utils
from cortex_profiles.internalprofilesclient import InternalProfilesClient
from cortex_profiles.schemas.dataframes import INSIGHT_COLS, INTERACTIONS_COLS, SESSIONS_COLS, \
    COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL
from cortex_profiles.schemas.dataframes import TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL
from cortex_profiles.schemas.schemas import INTERACTIONS
from cortex_profiles.synthetic import create_profile_synthesizer
from cortex_profiles.utils import namedtuple_asdict, json_makeup

visualization_client = ProfileVisualizationClient.from_current_cli_profile()
profiles_client = ProfilesClient.from_current_cli_profile()
internal_profiles_client = InternalProfilesClient.from_current_cli_profile()

def _ignore_unused_imports():
    any([
        implicit_attribute_builders,
        implicit_attribute_builder_utils,
        implicit_insight_attribute_builders,
        implicit_login_attribute_builders,
        profile_utils,
        utils,
        utils_for_dfs,
        INSIGHT_COLS,
        INTERACTIONS_COLS,
        SESSIONS_COLS,
        TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL,
        COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL,
        INTERACTIONS,
        namedtuple_asdict,
        json_makeup,
        create_profile_synthesizer,
        arrow,
        copy,
        Counter,
        np,
        pd,
        attr
    ])