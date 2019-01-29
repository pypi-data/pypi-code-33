# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import logging
import datetime
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode, b64decode
from dativa.tools.pandas import get_unique_column_name, datetime_to_string, string_to_datetime, format_string_is_valid
from .base import BaseAddIn, ScrubberValidationError, HistoryType

logger = logging.getLogger("dativa.scrubber.anonymization")

def _validate_key(key):
    try:
        RSA.importKey(key)
        return True
    except ValueError:
        return False


class EncryptionAddIn(BaseAddIn):
    """
    An addin that can be added to any BaseValidator class to provide encryption of the field
    """

    fields = {"encrypt": {"default": False, "validator": lambda x: x in [True, False]},
              "public_key": {"default": "none", "validator": _validate_key},
              "random_string": {"default": "random", "validator": lambda x: len(x) < 21},
              "random_string_date_field": {"default": "none", "validator": lambda x: True},
              "random_string_date_format": {"default": "none", "validator": format_string_is_valid},
              }

    def cross_validation(self):
        """
        Provides cross-validation for the fields in the encryption add-in
        """
        if self.validator.encrypt is True:
            if self.validator.public_key == "none":
                raise ScrubberValidationError("The param public_key must be set if encrypt is true")
            if self.validator.random_string_date_field != "none":
                if self.validator.random_string_date_format == "none":
                    raise ScrubberValidationError(
                        "random_string_date_format must be set is random_string_date_field is set")
                if not format_string_is_valid(self.validator.random_string):
                    raise ScrubberValidationError(
                        "{0} is not a valid value for random_string. This must be date parseable if "
                        "random_string_date_field is set".format(self.validator.random_string))

    @staticmethod
    def _pad(value, length):
        if len(value) > length:
            raise ScrubberValidationError(
                "random {0} is too long, should be no more than {1} bytes".format(value, length))
        return value + b'\00' * (length - len(value))

    def _get_encrypted(self, value, cipher, random):
        bytes_to_encrypt = str.encode(value, encoding="UTF-8")
        if random != b'random':
            # Update the random function directly within the cipher
            # as we want it to change with every record
            cipher._randfunc = lambda x: self._pad(random, x)

        encrypted_bytes = cipher.encrypt(bytes_to_encrypt)
        return str(b64encode(encrypted_bytes), encoding="UTF-8")

    def _encrypt(self, df, column):
        """
        Encrypts the passed column using RSA encryption with AOEP
        """
        public_key = RSA.importKey(self.validator.public_key)
        cipher = PKCS1_OAEP.new(public_key)

        # set up additional columns we will use
        cols = dict()
        cols["random_number"] = get_unique_column_name(df, "random", "_random")

        # get the random_string for each row
        if self.validator.random_string_date_field == "none":
            df[cols["random_number"]] = str.encode(self.validator.random_string, 'UTF-8')
        else:
            if self.validator.random_string_date_field not in df.columns:
                raise ScrubberValidationError(
                    "The random_string_date_field %s was not present in the passed DataFrame".format(
                        self.validator.random_string_date_field))
            else:
                dates = string_to_datetime(
                    df[self.validator.random_string_date_field], format=self.validator.random_string_date_format,
                    errors='coerce')
                df[cols["random_number"]] = datetime_to_string(dates, self.validator.random_string)
                df[cols["random_number"]] = df[cols["random_number"]].apply(lambda x: str.encode(x, 'UTF-8'))

        df[column] = df.apply(lambda row: self._get_encrypted(row[column], cipher, row[cols["random_number"]]), axis=1)

        if self.validator.random_string_date_field == "none":
            self.report_writer.log_history(
                self.validator.rule_type,
                column,
                df[column].to_frame(),
                HistoryType.MODIFIED,
                "Encrypted values")
        else:
            self.report_writer.log_history(
                self.validator.rule_type,
                column,
                df[[column, self.validator.random_string_date_field]],
                HistoryType.MODIFIED,
                "Encrypted values to date field")

        df.drop(cols["random_number"], axis=1, inplace=True)

    def run(self, df, column, original_column=None):
        """
        Runs the encryption add-in on the passed column
        """
        if self.validator.encrypt:
            self._encrypt(df, column)


class DecryptionAddIn(BaseAddIn):
    """
    An addin that can be added to any BaseValidator class to provide decryption of the field
    """

    fields = {"decrypt": {"default": False, "validator": lambda x: x in [True, False]},
              "private_key": {"default": "none", "validator": _validate_key}
              }

    def cross_validation(self):
        """
        Provides cross-validation for the decryption add-in
        """
        if self.validator.decrypt is True:
            if self.validator.private_key == "none":
                raise ScrubberValidationError("The param private_key must be set if decrypt is true")

    @staticmethod
    def _get_decrypted(value, cipher):
        bytes_to_decrypt = b64decode(str.encode(value, encoding="UTF-8"))
        decrypted_bytes = cipher.decrypt(bytes_to_decrypt)
        return str(decrypted_bytes, encoding="UTF-8")

    def _decrypt(self, df, column):
        """
        Decrypts the passed column using RSA encryption with AOEP
        """
        private_key = RSA.importKey(self.validator.private_key)
        cipher = PKCS1_OAEP.new(private_key)
        df[column] = df[column].apply(lambda message: self._get_decrypted(message, cipher))

        self.report_writer.log_history(
            self.validator.rule_type,
            column,
            df[column].to_frame(),
            HistoryType.MODIFIED,
            "Decrypted all values")

    def run(self, df, column, original_column=None):
        """
        Runs the decryption add-ing
        """
        if self.validator.decrypt:
            self._decrypt(df, column)


class HashingAddIn(BaseAddIn):
    """
    An addin that can be added to any BaseValidator class to provide hashing of the field
    """

    fields = {"hash": {"default": False, "validator": lambda x: x in [True, False]},
              "hash_length": {"default": 16, "validator": lambda x: 0 < x < 129},
              "salt": {"default": "none", "validator": lambda x: len(x) < 17},
              "salt_date_field": {"default": "none", "validator": lambda x: True},
              "salt_date_format": {"default": "none", "validator": format_string_is_valid},
              }

    def cross_validation(self):
        """
        Provides cross-validation on the fields passed to the hashing add-in
        """
        if self.validator.hash is True:
            if self.validator.salt_date_field != "none":
                if self.validator.salt_date_format != "none":
                    if format_string_is_valid(self.validator.salt):
                        salt = datetime_to_string(datetime.datetime.now(), self.validator.salt)
                        if len(salt) > 16:
                            raise ScrubberValidationError(
                                "Salt {0} is too long once the data is applied, maximum length 16 bytes".format(
                                    self.validator.salt))
                    else:
                        raise ScrubberValidationError(
                            "{0} is not a valid value for salt. This must be date parseable if salt_date_field is set".format(
                                self.validator.salt))
                else:
                    raise ScrubberValidationError("salt_date_format must be set if salt_date_field is set")

    def _get_hash(self, value, salt):
        """
        Gets the hash for the passed value with the specific salt
        """
        return hashlib.sha512(value + salt).hexdigest()[0:self.validator.hash_length]

    def _hash(self, df, column):
        """
        Hashes the passed column with the salt in the fields passed to the add-in
        """

        cols = dict()
        cols["salt"] = get_unique_column_name(df, "salt")
        cols["bytes"] = get_unique_column_name(df, "bytes")

        if self.validator.salt_date_field == "none":
            df[cols["salt"]] = str.encode(self.validator.salt, 'UTF-8')
        else:
            if self.validator.salt_date_field not in df.columns:
                raise ScrubberValidationError("The salt_date_field %s was not present in the passed DataFrame".format(
                    self.validator.salt_date_field))
            else:
                dates = string_to_datetime(df[self.validator.salt_date_field], format=self.validator.salt_date_format,
                                           errors='coerce')
                df[cols["salt"]] = datetime_to_string(dates, self.validator.salt).apply(
                    lambda x: str.encode(x, 'UTF-8'))

        df[cols["bytes"]] = df[column].apply(lambda x: str.encode(x, 'UTF-8'))
        df[column] = df.apply(lambda row: self._get_hash(row[cols["bytes"]], row[cols["salt"]]), axis=1)

        df.drop(cols["salt"], axis=1, inplace=True)
        df.drop(cols["bytes"], axis=1, inplace=True)

        if self.validator.salt_date_field == "none":
            self.report_writer.log_history(
                self.validator.rule_type,
                column,
                df[column].to_frame(),
                HistoryType.MODIFIED,
                "Hashed all values")
        else:
            self.report_writer.log_history(
                self.validator.rule_type,
                column,
                df[[self.validator.salt_date_field, column]],
                HistoryType.MODIFIED,
                "Hashed all values to salt date")

    def run(self, df, column, original_column=None):
        """
        Runs the hashing add-ing
        """
        if self.validator.hash:
            self._hash(df, column)
