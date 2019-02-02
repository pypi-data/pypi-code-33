"""
ml4k module
"""
import requests
from PIL import Image

BASE_URL = 'https://machinelearningforkids.co.uk/api/scratch/{api_key}'


class Model:
    """
    Represents a ML4K model with a given API key
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = BASE_URL.format(api_key=api_key)

    def classify(self, text):
        """
        Classify the given text using your model
        """
        url = self.base_url + '/classify'
        response = requests.get(url, params={'data': text})

        if not response.ok:
            response.raise_for_status()

        response_data = response.json()
        return response_data[0]
