"""
ml4k module
"""
import base64
import requests

BASE_URL = 'https://machinelearningforkids.co.uk/api/scratch/{api_key}'
DATA_LIMIT_MB = 2  # taxinomitis has a 3mb limit for base64-encoded data


class Model:
    """
    Represents a ML4K model with a given API key
    """
    def __init__(self, api_key, project_type='text'):
        self.api_key = api_key
        self.project_type = project_type
        self.base_url = BASE_URL.format(api_key=api_key)

    def classify(self, data):
        """
        Classify the given text using your model
        """
        url = self.base_url + '/classify'

        # if data is binary, check size limit and convert to base64
        if isinstance(data, bytes):
            data_limit = DATA_LIMIT_MB * 1024 * 1024
            if len(data) > data_limit:
                raise ValueError('Data must be less than {} MB'.format(DATA_LIMIT_MB))
            data = base64.b64encode(data).decode()

        # TODO: numbers data

        response = requests.post(url, json={'data': data})

        if not response.ok:
            response.raise_for_status()

        response_data = response.json()
        return response_data[0]
