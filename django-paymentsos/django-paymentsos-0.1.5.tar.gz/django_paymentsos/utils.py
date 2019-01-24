import hashlib
import hmac

from django_paymentsos.settings import paymentsos_settings as settings


def get_signature(*args):
    fmt = '{},{},{},{},{},{},{},{},{},{},{},{},{},{}'
    data = fmt.format(*args)
    return hmac.new(settings.PRIVATE_KEY.encode('utf'), data.encode('utf'), hashlib.sha256).hexdigest()
