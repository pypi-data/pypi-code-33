from marketo.rfc3339 import rfc3339
import hmac
import hashlib
import datetime


def sign(message, encryption_key):
    digest = hmac.new(encryption_key, message, hashlib.sha1)
    return digest.hexdigest().lower()


def header(user_id, encryption_key):
    timestamp = rfc3339(datetime.datetime.now())
    msg = timestamp + user_id
    signature = sign(msg.encode(), encryption_key)
    return (
        '<SOAP-ENV:Header><ns1:AuthenticationHeader>' +
              '<mktowsUserId>' + user_id + '</mktowsUserId>' +
              '<requestSignature>' + signature + '</requestSignature>' +
              '<requestTimestamp>' + timestamp + '</requestTimestamp>' +
        '</ns1:AuthenticationHeader></SOAP-ENV:Header>')
