import binascii
import logging
import os
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Optional

from ecdsa.util import sigdecode_der, sigdecode_string
from fastecdsa.curve import secp256k1
from fastecdsa.ecdsa import verify
from fastecdsa.point import Point
from motor import MotorClient, MotorDatabase
# noinspection PyProtectedMember
from motor.motor_tornado import MotorClientSession
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
from tornado.web import RequestHandler, HTTPError


# noinspection PyAbstractClass
class PMESAuthHandler(RequestHandler):
    """
    Handler used for PMES signature verification auth
    """
    _motor_client: MotorClient
    _motor_db: MotorDatabase
    _motor_session: MotorClientSession
    # Current user (accessible from self.current_user property)
    _current_user: Optional[str]
    # Time when authentication started
    _start_datetime: datetime

    # Grace period for "future" request (i.e. if user clock is ahead by 10 seconds)
    GRACE_PERIOD: timedelta = timedelta(minutes=int(os.getenv('GRACE_PERIOD', 1440)))
    # Expiration period of the signature
    EXPIRATION_PERIOD: timedelta = timedelta(minutes=int(os.getenv('EXPIRATION_PERIOD', 1440)))
    # Whether to display exception info in errors
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    # MongoDB connection URI
    MONGODB_URI: str = os.getenv('MONGODB_URI')
    # MongoDB database name
    DB_NAME = 'sessions'

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

    async def prepare(self):
        """
        Stores current user in self.current_user
        """
        # Initialize Motor
        self._motor_client = MotorClient(self.MONGODB_URI)
        self._motor_session = await self._motor_client.start_session()
        self._motor_db = self._motor_client[self.DB_NAME]
        await self._create_indexes()

        self._current_user = await self.get_current_user_async()

    async def _create_indexes(self):
        """
        Creates a TTL index on collection 'used_signatures' for field 'timestamp'
        Also creates a unique index on 'signature' and 'public_key' fields
        """
        ttl_period = self.EXPIRATION_PERIOD.total_seconds()

        await self._motor_db.used_signatures.create_index('timestamp',
                                                          expireAfterSeconds=int(ttl_period),
                                                          session=self._motor_session)

        await self._motor_db.used_signatures.create_index([('signature', ASCENDING),
                                                           ('public_key', ASCENDING)],
                                                          unique=True,
                                                          session=self._motor_session)

    async def get_current_user_async(self) -> Optional[str]:
        """
        Verifies signature from headers, returns user's public key if signature is valid
        :return: public key of the current user (or None if auth failed)
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
            return None

        if len(public_key) not in (128, 130):
            logging.warning(f'Invalid public key length: {len(public_key)}')
            return None

        try:
            signature_datetime = datetime.fromisoformat(timestamp)
        except ValueError as e:
            logging.warning(f'Invalid timestamp format: {str(e)}')
            return None

        if self._is_expired(signature_datetime):
            logging.warning('Signature has already expired')
            return None

        if not self._verify(public_key, signature, timestamp):
            logging.warning(f'Signature is invalid: {signature}')
            return None

        try:
            await self._save_signature(public_key, signature, signature_datetime)
        except DuplicateKeyError as e:
            logging.warning(f'Signature was already used: {str(e)}')
            return None

        return public_key

    def _is_expired(self, timestamp: datetime) -> bool:
        """
        Check if signature has expired
        (grace period also given so that requests "from the future" are also valid)
        :param timestamp: timestamp of the signature
        :return: True if expired
        """
        delta = self._start_datetime - timestamp
        logging.debug(f'Timestamp check delta: {delta}')
        return delta > self.EXPIRATION_PERIOD or delta < -self.GRACE_PERIOD

    async def _save_signature(self, public_key: str, signature: str, timestamp: datetime):
        """
        Checks whether this signature was already used before
        :param public_key: public key
        :param signature: signature
        :param timestamp: timestamp
        """
        collection = self._motor_db.used_signatures
        document = {'public_key': public_key, 'signature': signature, 'timestamp': timestamp}
        await collection.insert_one(document, session=self._motor_session)

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

        # Transform public key from string to a point
        public_key = bytes.fromhex(public_key)
        x = int(binascii.hexlify(public_key[:32]), 16)
        y = int(binascii.hexlify(public_key[32:]), 16)
        public_key = Point(x, y, curve=secp256k1)

        # Get r, s from signature string
        signature = bytes.fromhex(signature)
        if len(signature) == 128:
            r, s = sigdecode_string(signature, secp256k1.p)
        else:
            r, s = sigdecode_der(signature, secp256k1.p)

        return verify((r, s), message, public_key, curve=secp256k1, hashfunc=sha256)
