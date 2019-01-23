from __future__ import absolute_import

import pandas

from aiotstudio._core.types import mql_result_to_pandas_dataframe
from aiotstudio._core.client import get_default_client
from aiotstudio._core import services

_client = get_default_client()


def to_json(query):
    # type: (dict) -> dict
    """Execute a MQL query, returns the result as a JSON object

    Args:
        query (dict): MQL query to be run on the platform

    Returns:
        dict: Result of the query as in JSON 
        
    Example:
        >>> from aiotstudio.search import to_json
        >>> to_json({ "from": "event", "select": [ {"count": "*"} ] })
        {'columns': [{'label': 'COUNT(*)', 'type': 'long'}], 'rows': [[877]]}

    See Also:
        `Search API </documentation/api_search.html>`_
    """

    return services.restitution_search(_client, query)


def to_pandas(query):
    # type: (dict) -> pandas.DataFrame
    """Execute a MQL query, returns the result as a Pandas DataFrame

    Args:
        query (dict): MQL query to be run on the platform

    Returns:
        pandas.DataFrame: Result of the query as a pandas dataframe

    Example:
        >>> from aiotstudio.search import to_pandas
        >>> to_pandas({ "from": "event", "select": [ {"count": "*"} ] })
            COUNT(*)
        0	877

    See Also:
        - `Search API </documentation/api_search.html>`_
        - `Pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_
    """
    return mql_result_to_pandas_dataframe(to_json(query))[:100000]
