#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from pacifica.policy.status.proposal.by_user import ProposalUserSearch
from pacifica.policy.status.proposal.search import ProposalKeywordSearch
from pacifica.policy.status.proposal.lookup import ProposalLookup


# pylint: disable=too-few-public-methods
class ProposalQuery(object):
    """CherryPy root object class."""

    exposed = False

    def __init__(self):
        """Create local objects for sub tree items."""
        self.by_user_id = ProposalUserSearch()
        self.search = ProposalKeywordSearch()
        self.by_proposal_id = ProposalLookup()
# pylint: enable=too-few-public-methods
