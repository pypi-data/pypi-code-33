from .AbstractModel import AbstractFunction


class Multiply(AbstractFunction):

    function_name = "AIOS Multiply Function"
    deployment_name = "AIOS Multiply Function Deployment"

    def publish_to_wml(self, wml_client):

        def score(payload):
            values = [[row[0] * row[1]] for row in payload['values']]
            return {'fields': ['multiplication'], 'values': values}

        return wml_client.repository.store_function(score, self.function_name)

    def get_model_props(self, wml_client):
        pass

    def get_scoring_payload(self):
        pass