import sys
import time, base64
from itertools import cycle
import aether_shared.sharedconfig as cfg
from oauth2client.service_account import ServiceAccountCredentials

class user_api_utils(object):

    @staticmethod
    def user_stub_to_signed_url(stub):
        """Transform a user:// stub to an https://storage.googleapis.com signed url."""
        # user://W30yqP7xHgf1kBAghBSyVG8B6Xl1/82cb0b416c930d41f91c3a79a4abced4_2017-11-18_LANDSAT_8.tif
        # The structure is user://(uuid encrypted)/(blob name)
        bucket = cfg._cloud_filesystem_user_bucket
        blob_name = stub[7:]
        return user_api_utils.google_signature_sign(bucket, blob_name)

    @staticmethod
    def gs_stub_to_url(stub):
        """Transform a gs:// stub to an https://storage.googleapis.com url."""
        # gs://gcp-public-data-landsat/LC08/01/039/037/LC08_L1TP_039037_20171118_20171205_01_T1
        # to https://storage.googleapis.com/(bucket)/(blob_name)
        bucket = stub.split("/")[2]
        blob_name = "/".join(stub.split("/")[3:])
        return "https://storage.googleapis.com/{bucket}/{blob_name}".format(bucket=bucket, blob_name=blob_name)

    class vigenere_cipher(object):

        _ALPHA = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        _len_alpha = len(_ALPHA)

        _key = "uuidpasswordkey"

        def encrypt(self, plaintext):
            """Encrypt the string and return the ciphertext"""
            pairs = zip(plaintext, cycle(self._key))
            result = ''

            for pair in pairs:
                total = reduce(lambda x, y: self._ALPHA.index(x) + self._ALPHA.index(y), pair)
                result += self._ALPHA[total % self._len_alpha]

            return result

        def decrypt(self, ciphertext):
            """Decrypt the string and return the plaintext"""
            pairs = zip(ciphertext, cycle(self._key))
            result = ''

            for pair in pairs:
                total = reduce(lambda x, y: self._ALPHA.index(x) - self._ALPHA.index(y), pair)
                result += self._ALPHA[total % self._len_alpha]

            return result

    class rc_updating_format_text(object):

        def __init__(self, format_text):
            self.format_text = format_text

        def change_format_text(self, format_text):
            self.format_text = format_text

        def to_print(self, args=None, finished=False):
            text = self.format_text if args is None else self.format_text.format(**args)
            if finished:
                text += "\n"
            sys.stdout.write("\r{}".format(text))
            sys.stdout.flush()

    class rc_streaming_text(object):

        def __init__(self, text):
            self.text = text
            self.index = 0

        def change_text(self, text):
            self.text = text

        def print_next(self):
            self.index = 0 if self.index >= len(self.text) else self.index + 1
            to_print = "" if self.index == 0 else self.text[:self.index]
            sys.stdout.write("\r{}".format(to_print))
            sys.stdout.flush()

        def print_finished(self):
            sys.stdout.write("\r{}\n".format(self.text))
            sys.stdout.flush()

    # bucket = "ae_platform_user_responses"
    # blob_name = "W30yqP7xHgf1kBAghBSyVG8B6Xl1/82cb0b416c930d41f91c3a79a4abced4_2017-12-27T18%3A33%3A03.460000Z_SENTINEL_2A.tif"
    # Add url to proto & search + crop + download values. + flag for download.
    @staticmethod
    def google_signature_sign(bucket, blob_name, method="GET", expiration_seconds=3.14e7):
        """Creates a signed signature link for any object in Google Cloud Storage."""

        # Notice that this method uses a certification that is *different* that the Google Storage Admin certification,
        # and does so using a certificate which as only Google Storage Read permissions.
        def google_signature_string_replace(s):
            s = s.replace("+", "%2B")
            s = s.replace("/", "%2F")
            return s

        expiration = str(int(time.time() + expiration_seconds))
        signature_components = [
            method, # HTTP_VERB of the client making the request for the object
            "", # MD5 hash of object in the cloud
            "", # Content-Type of the object: usually "application/octet-stream" for how the platform uploads TIF objects
            expiration,
            "/{}/{}".format(bucket, blob_name)
        ]

        _signature_sign_certification_filename = "certificates/aether-user-signed-url-service.json"
        signature_string = "\n".join(signature_components)
        creds = ServiceAccountCredentials.from_json_keyfile_name(_signature_sign_certification_filename)
        client_id = creds.service_account_email
        signature = creds.sign_blob(signature_string)[1]
        encoded_signature = google_signature_string_replace(base64.b64encode(signature))

        base_url = "https://storage.googleapis.com/{bucket}/{blob_name}".format(bucket=bucket, blob_name=blob_name)
        url_signature = "?GoogleAccessId={google_access_storage_id}&Expires={expiration}&Signature={encoded_signature}".format(
            google_access_storage_id=client_id,
            expiration=expiration,
            encoded_signature=encoded_signature
        )

        full_url = "{base_url}{url_signature}".format(base_url=base_url, url_signature=url_signature)
        return full_url
