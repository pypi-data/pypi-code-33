import requests


def serve(tokens, dataset, resource_id, delivery_channel="http", delivery_format="csv_headers", language="en-US"):
    request = {
        "tokens": tokens,
        "dataset": dataset,
        "resource_id": resource_id,
        "delivery_channel": delivery_channel,
        "delivery_format": delivery_format,
        "language": language
    }
    r = requests.post("https://tgmkha9n7e.execute-api.eu-west-1.amazonaws.com/Dev/serve/", json=request)
    return r.json()