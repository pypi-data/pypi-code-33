#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from pacifica.policy.status.instrument.by_proposal_id import InstrumentsByProposal
from pacifica.policy.status.instrument.search import InstrumentKeywordSearch


# pylint: disable=too-few-public-methods
class InstrumentQuery(object):
    """CherryPy root object class."""

    exposed = False

    def __init__(self):
        """Create local objects for sub tree items."""
        # self.search = ProposalSearch()
        self.by_proposal_id = InstrumentsByProposal()
        self.search = InstrumentKeywordSearch()
