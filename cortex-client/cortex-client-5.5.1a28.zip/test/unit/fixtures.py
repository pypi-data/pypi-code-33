

def john_doe_token():
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'


def john_doe_subject():
    return '1234567890'


def build_mock_url(uri, version=3):
    return "{api_endpoint}/v{version}/{uri}".format(api_endpoint=mock_api_endpoint(), version=version, uri=uri)


def mock_api_endpoint():
    return 'http://1.2.3.4:8000'
