import json

from ..const import API_OPERATIONS, API_PATH
from .base import Resource
from .experiments import Experiments
from .personalise_result_wrapper import PersonaliseResultWrapper


class Campaign(Resource):
    PATH = API_PATH["campaigns.campaign"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.experiments = Experiments(
            self, API_PATH["experiments"], API_OPERATIONS["experiments"]
        )

    def personalise(self, pubkey, secretkey, abvariant=None, signals={}, limit=5):
        """Returns campaign personalisation

        ```
        campaign.personalise(abvariant_label='A', signals=['key1', 'key2'], limit=15)
        ```

        :param abvariant_label: abvariant to be used for personalisation
        :type abvariant_label: string

        :param limit: maximum number of results to be retrieved
        :type limit: int

        :param signals: signals to be triggered during personalisation
        :type signals: dictionary

        :return: PersonaliseResults
        """

        params = {"limit": limit, "signals": json.dumps(signals), "campaign": self.key}

        if abvariant is not None:
            params["abvariant"] = abvariant

        headers = self.root._connection.hmac_header(pubkey, secretkey)

        params = {k: v for k, v in params.items() if v}

        result_json = self.root._dispatch_request(
            caller=self,
            operation="PERSONALISE",
            path="personalise",
            params=params,
            headers=headers,
        )

        return PersonaliseResultWrapper(**result_json)
