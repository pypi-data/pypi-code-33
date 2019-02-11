from .keys import SIGN_PUB_KEY, SIGN_PRV_KEY

from qtum_utils.qtum import Qtum


def verify(func):
    async def wrapper(*args, **kwargs):

        message = kwargs.get("message")
        signature = kwargs.get("signature")
        try:
            flag = Qtum.verify_message(message, signature, SIGN_PUB_KEY)
        except:
            flag = None
        if not flag:
            result = {"error": 403, "reason": "Invalid signature"}
        else:
            result = await func(*args, **kwargs)
        return result
    return wrapper
