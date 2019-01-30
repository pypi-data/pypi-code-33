#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from pacifica.policy.config import get_config
from pacifica.policy.status.base import QueryBase


# pylint: disable=too-few-public-methods
class ProposalKeywordSearch(QueryBase):
    """Retrieves a set of proposals for a given keyword set."""

    exposed = True

    def _get_proposals_for_keywords(self, user_id, search_terms=None):
        """Return a list with all the proposals involving this user."""
        is_admin = self._is_admin(user_id) if user_id is not None else False
        if not search_terms and user_id:
            # no terms, just get any proposals for this user
            md_url = '{0}/proposalinfo/by_user_id/{1}'.format(
                get_config().get('metadata', 'endpoint_url'), user_id)
        else:
            md_url = '{0}/proposalinfo/search/{1}'.format(
                get_config().get('metadata', 'endpoint_url'), search_terms)

        results = []

        response = requests.get(url=md_url)
        if int(response.status_code / 100) == 2:
            if is_admin:
                results = response.json()
            else:
                available_proposals = QueryBase._get_available_proposals(
                    user_id)
                results = [x for x in response.json() if x.get('id')
                           in available_proposals]

        return results

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @tools.json_out()
    def GET(self, search_terms=None, **kwargs):
        """CherryPy GET method."""
        user_id = kwargs['user'] if 'user' in kwargs else None
        return self._get_proposals_for_keywords(user_id, search_terms)
# pylint: enable=too-few-public-methods
