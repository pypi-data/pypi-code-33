
class DeploymentTemplate:
    asset_name = ""
    deployment_name = ""

    asset_uid = None
    deployment_uid = None

    def _deploy_model_to_wml(self, wml_client):
        raise NotImplementedError("Please Implement this method")

    def get_model_props(self, wml_client):
        pass

    def get_scoring_payload(self):
        raise NotImplementedError("Please Implement this method")

    def publish_to_wml(self, wml_client, delete_existing=False):
        asset_uid = None
        deployment_uid = None

        wml_models = wml_client.repository.get_details()
        wml_deployments = wml_client.deployments.get_details()

        for asset in wml_models['models']['resources']:
            if self.asset_name == asset['entity']['name']:
                asset_uid = asset['metadata']['guid']
                break

        for asset in wml_models['functions']['resources']:
            if self.asset_name == asset['entity']['name']:
                asset_uid = asset['metadata']['guid']
                break

        if delete_existing and asset_uid is not None:
            for deployment in wml_deployments['resources']:
                if 'published_model' in deployment['entity'] and asset_uid == deployment['entity']['published_model']['guid']:
                    print("Deleting deployment: {}".format(deployment['metadata']['guid']))
                    wml_client.deployments.delete(deployment['metadata']['guid'])
            wml_client.repository.delete(asset_uid)
            print("Deleting model: {}".format(asset_uid))
            asset_uid = None

        if asset_uid is None:
            print("Storing asset {}".format(self.asset_name))

            published_model_details = self._deploy_model_to_wml(wml_client)
            asset_uid = wml_client.repository.get_model_uid(published_model_details)

            print("Asset stored.")
        else:
            print("Found asset {} with ID: {}".format(self.asset_name, asset_uid))

        model_details = wml_client.repository.get_details(asset_uid)
        print("Model details:\n{}".format(model_details))

        for deployment in wml_deployments['resources']:
            if 'published_model' in deployment['entity'] and asset_uid == deployment['entity']['published_model']['guid']:
                deployment_uid = deployment['metadata']['guid']
                break

        if deployment_uid is None:
            print("Deploying model: {}, deployment name: {}".format(self.asset_name, self.deployment_name))

            deployment = wml_client.deployments.create(artifact_uid=asset_uid, name=self.deployment_name, asynchronous=False)
            deployment_uid = wml_client.deployments.get_uid(deployment)

            print("Deployment finished.")

        deployment_details = wml_client.deployments.get_details(deployment_uid)
        print("Deployment details:\n{}".format(deployment_details))

        self.asset_uid = asset_uid
        self.deployment_uid = deployment_uid