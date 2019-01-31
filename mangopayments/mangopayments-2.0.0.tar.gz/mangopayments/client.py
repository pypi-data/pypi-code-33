from django.conf import settings
from mangopay.api import APIRequest
import mangopay
from mangopay.auth import StaticStorageStrategy


def get_handler():

    mangopay.client_id = settings.MANGOPAY_CLIENT_ID
    mangopay.passphrase = settings.MANGOPAY_PASSPHRASE
    mangopay.sandbox = settings.MANGOPAY_SANDBOX

    handler = APIRequest(sandbox=settings.MANGOPAY_SANDBOX, storage_strategy=StaticStorageStrategy())

    return handler
