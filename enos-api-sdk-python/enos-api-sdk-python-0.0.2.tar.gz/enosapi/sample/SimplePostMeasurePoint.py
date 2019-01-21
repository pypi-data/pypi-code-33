from enosapi.request.PostMeasurepointsEnOSRequest import PostMeasurepointsEnOSRequest
from enosapi.client.EnOSDefaultClient import EnOSDefaultClient
import time
import json

enos_api_url = "https://{HOST}/enosapi/"

# the application configuration created in console
access_key = "ACCESS_KEY"
secret_key = "SECRET_KEY"

# sub-device parameters
device_asset_id = 'DEVICE_ASSET_ID'
product_key = 'PRODUCT_KEY'

# OU ID
org_id = "OU_ID"

if __name__ == "__main__":
    timestamp = int(time.time() * 1000)  # timestamp in milliseconds
    struct_measure_point = {'RawImage': 'local://file1',
                            'ProcessedImage': 'local://file2',
                            'Sensor': 'PM10',
                            'UpperLimit': 100,
                            'Value': 120,
                            'AlertFlag': 1,
                            'AlertMessage': 'PM10 over limit'}

    measure_points = {
        'Image': struct_measure_point
    }

    data = [{
        'measurepoints': measure_points,
        'assetId': device_asset_id,
        'time': timestamp
    }]

    param = {
        "data": json.dumps(data)
    }

    # two files named apple.png and orange.png should be put into the same directory as this code file
    file_to_upload = {"file1": open("apple.png", 'rb'), "file2": open("orange.png", 'rb')}

    request = PostMeasurepointsEnOSRequest(org_id=org_id, product_key=product_key, params=param,
                                           upload_file=file_to_upload)

    enos_api_client = EnOSDefaultClient(enos_api_url, access_key, secret_key)

    response = enos_api_client.execute(request)
    print(response)
