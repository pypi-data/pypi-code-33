"""
ml4k module
"""
import io
import base64
import requests
from PIL import Image

BASE_URL = 'https://machinelearningforkids.co.uk/api/scratch/{api_key}'
DATA_LIMIT_MB = 2  # taxinomitis has a 3mb limit for base64-encoded data


def optimize_image(image):
    output = io.BytesIO()
    image.thumbnail((1920, 1920), Image.ANTIALIAS)
    image.save(output, optimize=True, quality=85, format=image.format)
    return output.getvalue()


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

        # Handle binary data
        if isinstance(data, bytes):
            data_limit = DATA_LIMIT_MB * 1024 * 1024

            # Check if data is an image and try to optimize it if it's too big.
            try:
                image = Image.open(io.BytesIO(data))
            except IOError:
                pass
            else:
                if len(data) > data_limit:
                    data = optimize_image(image)

            # Ensure final data is within the size limit
            if len(data) > data_limit:
                raise ValueError('Data must be less than {} MB'.format(DATA_LIMIT_MB))

            # Convert to Base64
            data = base64.b64encode(data).decode()

        # TODO: numbers data

        response = requests.post(url, json={'data': data})

        if not response.ok:
            response.raise_for_status()

        response_data = response.json()
        return response_data[0]
