import logging
import os
from datetime import datetime, timedelta
from hashlib import sha256

import ecdsa
from ecdsa.keys import BadSignatureError
from tornado.web import RequestHandler, HTTPError


# noinspection PyAbstractClass
class PMESAuthHandler(RequestHandler):
    GRACE_PERIOD: timedelta = timedelta(minutes=-int(os.getenv('GRACE_PERIOD', 1)))
    EXPIRATION_PERIOD: timedelta = timedelta(minutes=int(os.getenv('EXPIRATION_PERIOD', 5)))
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'

    _start_datetime: datetime

    @staticmethod
    def _verify(public_key: str, signature: str, message: str) -> bool:
        """
        Verify signature using public key and message
        :param public_key: public key
        :param signature: signature
        :param message: message (timestamp)
        :return: True if signature is valid
        """
        if len(public_key) == 130:
            public_key = public_key[2:]

        try:
            vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key),
                                                curve=ecdsa.SECP256k1,
                                                hashfunc=sha256)
        except AssertionError:
            return False

        if len(signature) == 128:
            sigdecode = ecdsa.util.sigdecode_string
        else:
            sigdecode = ecdsa.util.sigdecode_der

        try:
            return vk.verify(bytes.fromhex(signature), message.encode(), sigdecode=sigdecode)
        except BadSignatureError as e:
            return False

    def _is_expired(self, timestamp: datetime) -> bool:
        """
        Check if signature has expired
        (grace period also given so that requests "from the future" are also valid)
        :param timestamp: timestamp of the signature
        :return: True if expired
        """
        delta = self._start_datetime - timestamp
        logging.debug(f'Timestamp check delta: {delta}')
        return delta > self.EXPIRATION_PERIOD or delta < self.GRACE_PERIOD

    def write_error(self, status_code: int, **kwargs):
        """
        Custom error page - JSON with 'error' and 'reason' fields.
        :param status_code: HTTP status code
        :param kwargs: needs to have exc_info
        :return: None
        """
        exc_class, exc, traceback = kwargs.get('exc_info')

        if isinstance(exc, HTTPError):
            reason = exc.log_message
        else:
            reason = str(exc) if self.DEBUG else 'Unknown error'

        self.finish({'error': status_code, 'reason': reason})

    def get_current_user(self) -> str:
        """
        Verifies signature from headers, returns user's public key if signature is valid
        :raises HTTPError: on errors
        :return: public key of the current user
        """
        self._start_datetime = datetime.utcnow()
        logging.debug(f'Initiating authentication, current timestamp: {self._start_datetime.isoformat()}')

        public_key = self.request.headers.get('PMES-Public-Key')
        signature = self.request.headers.get('PMES-Signature')
        timestamp = self.request.headers.get('PMES-Timestamp')

        logging.debug(f'PMES-Public-Key: {public_key}')
        logging.debug(f'PMES-Timestamp: {timestamp}')

        if None in (public_key, signature, timestamp):
            logging.warning('Missing one or more auth headers')
            raise HTTPError(401, 'Missing auth headers')

        if len(public_key) not in (128, 130):
            logging.warning(f'Invalid public key length: {len(public_key)}')
            raise HTTPError(401, 'Invalid public key')

        try:
            signature_datetime = datetime.fromisoformat(timestamp)
        except ValueError as e:
            logging.warning(f'Invalid timestamp format: {str(e)}')
            raise HTTPError(401, 'Invalid timestamp format')

        if self._is_expired(signature_datetime):
            logging.warning('Signature has already expired')
            raise HTTPError(401, 'Signature expired')

        if not self._verify(public_key, signature, timestamp):
            logging.warning(f'Signature is invalid: {signature}')
            raise HTTPError(401, 'Invalid signature')

        return public_key
