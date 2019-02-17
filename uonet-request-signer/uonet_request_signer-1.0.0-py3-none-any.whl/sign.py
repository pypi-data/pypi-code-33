# -*- coding: utf-8 -*-

from OpenSSL import crypto
import base64
import json


def sign_content(password, certificate, content):
    encoding = "utf-8"
    content_string = (
        json.dumps(content).encode(encoding)
        if isinstance(content, dict) or isinstance(content, list)
        else str(content).encode(encoding)
    )
    p12 = crypto.load_pkcs12(base64.b64decode(certificate), password.encode(encoding))
    signed = crypto.sign(p12.get_privatekey(), content_string, "RSA-SHA1")
    return base64.b64encode(signed).decode(encoding)
