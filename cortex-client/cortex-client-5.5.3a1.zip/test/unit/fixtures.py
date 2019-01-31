

def john_doe_token():
    return 'eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJ0ZW5hbnQiOiJBY21lIEluYy4ifQ.ky4VnJ8kZnShc1Tk6oqat1SYUvSeiCMD3_GWckrKPJFq600Y-Zxa1lZi_YLuHRX6'


def john_doe_subject():
    return '1234567890'


def build_mock_url(uri, version=3):
    return "{api_endpoint}/v{version}/{uri}".format(api_endpoint=mock_api_endpoint(), version=version, uri=uri)


def mock_api_endpoint():
    return 'http://1.2.3.4:8000'
