from contextlib import contextmanager


@contextmanager
def managed_token_django(client, model=None, token_str=None,
                         refresh_token_str=None, expiration_str=None,
                         model_dict=None):
    # Enter code
    if model is not None:
        if token_str is None or refresh_token_str is None:
            raise TypeError("model was specified, but token or refresh token"
                            " not")
    elif model_dict is not None:
        token_str = model_dict["token"]
        refresh_token_str = model_dict["refresh_token"]
        model = model_dict["model"]
        expiration_str = model_dict.get("expiration", None)
    else:
        raise TypeError("model or model_dict were not secified")

    client.token_managed = True
    client._token_str = token_str
    client._refresh_token_str = refresh_token_str
    client._model = model
    yield
    # Exit code
    client.token_managed = False
    setattr(model, token_str, client._singular_token)
    setattr(model, refresh_token_str, client._refresh_token)
    if expiration_str is not None:
        setattr(model, expiration_str, client._expiration)
    model.save()
