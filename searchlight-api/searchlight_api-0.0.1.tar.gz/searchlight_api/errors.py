class CredentialsMissingError(Exception):
    def __init__(self, token):
        assert token in ["Searchlight API Key",
                         "Searchlight Shared Secret"], "Not a valid token arg"
        message = "{token} required. If you have one " \
                  "either add it to environment as {env} " \
                  "or pass it as the api_key parameter. If you do" \
                  " not have one you can request one here: " \
                  "http://developers.conductor.com/".\
            format(token=token, env=token.replace(" ", "_").upper())
        Exception.__init__(self, message)
