# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod


class AbstractModel(ABC):
    model_name = ""
    deployment_name = ""

    @abstractmethod
    def publish_to_wml(self, wml_client):
        pass

    @abstractmethod
    def get_model_props(self, wml_client):
        pass

    @abstractmethod
    def get_scoring_payload(self):
        pass

    def deploy_to_wml(self, wml_client):
        model_uid = None
        deployment_uid = None

        wml_models = wml_client.repository.get_details()

        for model in wml_models['models']['resources']:
            if self.model_name == model['entity']['name']:
                model_uid = model['metadata']['guid']
                break

        if model_uid is None:
            print("Storing model {}".format(self.model_name))

            published_model_details = self.publish_to_wml(wml_client)
            model_uid = wml_client.repository.get_model_uid(published_model_details)

            print("Model stored.")

        model_details = wml_client.repository.get_details(model_uid)
        print("Model details:\n{}".format(model_details))

        wml_deployments = wml_client.deployments.get_details()
        for deployment in wml_deployments['resources']:
            if 'published_model' in deployment['entity'] and model_uid == deployment['entity']['published_model']['guid']:
                deployment_uid = deployment['metadata']['guid']
                break

        if deployment_uid is None:
            print("Deploying model: {}, deployment name: {}".format(self.model_name, self.deployment_name))

            deployment = wml_client.deployments.create(artifact_uid=model_uid, name=self.deployment_name, asynchronous=False)
            deployment_uid = wml_client.deployments.get_uid(deployment)

            print("Deployment finished.")

        deployment_details = wml_client.deployments.get_details(deployment_uid)
        print("Deployment details:\n{}".format(deployment_details))

        return model_uid, deployment_uid


class AbstractFunction(ABC):
    function_name = ""
    deployment_name = ""

    @abstractmethod
    def publish_to_wml(self, wml_client):
        pass

    @abstractmethod
    def get_model_props(self, wml_client):
        pass

    @abstractmethod
    def get_scoring_payload(self):
        pass

    def deploy_to_wml(self, wml_client):
        model_uid = None
        deployment_uid = None

        wml_models = wml_client.repository.get_details()

        for model in wml_models['functions']['resources']:
            if self.function_name == model['entity']['name']:
                model_uid = model['metadata']['guid']
                break

        if model_uid is None:
            print("Storing function {}".format(self.function_name))

            published_function_details = self.publish_to_wml(wml_client)
            model_uid = published_function_details['metadata']['guid']

            print("Model stored.")

        wml_deployments = wml_client.deployments.get_details()

        for deployment in wml_deployments['resources']:
            if 'published_model' in deployment['entity'] and model_uid == deployment['entity']['published_model']['guid']:
                deployment_uid = deployment['metadata']['guid']
                break
            elif 'deployable_asset' in deployment['entity'] and model_uid == deployment['entity']['deployable_asset']['guid']:
                deployment_uid = deployment['metadata']['guid']
                break

        if deployment_uid is None:
            print("Deploying model: {}, deployment name: {}".format(self.function_name, self.deployment_name))

            deployment = wml_client.deployments.create(artifact_uid=model_uid, name=self.deployment_name, asynchronous=False)
            deployment_uid = wml_client.deployments.get_uid(deployment)

            print("Deployment finished.")

        return model_uid, deployment_uid


class AbstractFeedbackModel(ABC):

    @abstractmethod
    def publish_to_wml(self, wml_client, db2_credentials):
        pass

    @abstractmethod
    def get_model_props(self, wml_client, db2_credentials):
        pass

    @abstractmethod
    def get_training_data_reference(self, db2_credentials):
        pass

    @abstractmethod
    def get_feedback_data(self):
        pass

    @abstractmethod
    def get_scoring_payload(self):
        pass
