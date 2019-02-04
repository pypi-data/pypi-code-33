import requests
import base64


def request_new_access_token(session):
    url = "{token_issuer_host}/v1/{token_issuer_path}".format(
        token_issuer_host=session.token_issuer_host,
        token_issuer_path=session.token_issuer_path
    )
    headers = {
        "Authorization": "Basic {}".format(base64.b64encode(
            (session.api_key + ":" + session.api_secret
             ).encode("ascii")).decode("ascii")
        )
    }

    data = {
        "grant_type": "password",
        "username": session.username,
        "password": session.password
    }
    response = requests.post(url=url, headers=headers, data=data)
    if response and response.status_code == requests.codes["ok"]:
        response_json = response.json()
        session.access_token = response_json["access_token"]
        return session.access_token
    return None
