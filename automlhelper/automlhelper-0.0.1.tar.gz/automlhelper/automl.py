from google.cloud import automl_v1beta1 as automl

class AutoML:

    def __init__(self, project_id, compute_region='us-central1', model_id=''):
        self.project_id = project_id
        self.compute_region = compute_region
        
        self.client = automl.AutoMlClient()
        self.project_location = self.client.location_path(
            project_id, compute_region)
        
        if model_id == '':
            model = self.get_last_model()
            self.model_id = model.name.split("/")[-1]
        else:
            self.model_id = model_id

    def get_tag_evaluation(self, model_id = ''):
        if model_id == '':
            model_id = self.model_id
        
        model_full_id = self.client.model_path(
            self.project_id, self.compute_region, model_id)
        response = self.client.list_model_evaluations(model_full_id)
        results = []
        
        for r in response:
            results.append(r)
        return results

    def get_predictions(self, image_bytes, model_id='', score_threshold= u'0.10'):
        if model_id == '':
            model_id = self.model_id

        model_full_id = self.client.model_path(
            self.project_id, self.compute_region, model_id)
        
        prediction_client = automl.PredictionServiceClient()
        
        payload = {"image": {"image_bytes": image_bytes}}
        params = {}
        if score_threshold:
            params = {"score_threshold": score_threshold}

        result = []
        predictions = prediction_client.predict(model_full_id, payload, params)
        
        for p in predictions.payload:
            result.append((p.display_name, p.classification.score))
        
        return sorted(result, key=lambda _ : _[1], reverse=True)

    def get_last_dataset(self, filter_ = ''):
        response = self.client.list_datasets(self.project_location, filter_)
        return sorted(response, key=lambda _: _.create_time.seconds, reverse=True)[0]
    
    def get_last_model(self):
        response = self.client.list_models(self.project_location)
        return sorted(response, key=lambda _: _.create_time.seconds, reverse=True)[0]