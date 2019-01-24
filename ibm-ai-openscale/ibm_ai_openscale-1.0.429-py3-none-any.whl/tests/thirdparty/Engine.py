# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod


class Engine(ABC):

    latest_request = None
    latest_response = None
    latest_response_time = None

    @abstractmethod
    def score(self, binding_details, subscription_details):
        pass

    def get_latest_scoring(self):
        return self.latest_request, self.latest_response, self.latest_response_time
