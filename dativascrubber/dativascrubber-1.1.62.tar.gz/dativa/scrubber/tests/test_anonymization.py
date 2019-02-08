# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

from dativa.tools.pandas import CSVHandler
from dativa.scrubber.tests import _BaseTest
from dativa.scrubber import Scrubber, ScrubberValidationError


class AnonymizationTests(_BaseTest):

    def test_errors_hash(self):
        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "hash": True,
                                      "salt": "A9788@%y%m%d",
                                      "salt_date_field": "date"
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "hash": True,
                                      "salt": "A9788@",
                                      "salt_date_field": "date",
                                      "salt_date_format": "%Y-%m-%d %H:%M:%S"
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "hash": True,
                                      "salt": "1234567891%Y%m%d",
                                      "salt_date_field": "date",
                                      "salt_date_format": "%Y-%m-%d %H:%M:%S"
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "hash": True,
                                      "salt": "A9788@%y%m%d",
                                      "salt_date_field": "data",
                                      "salt_date_format": "%Y-%m-%d %H:%M:%S"
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

    def test_errors_encrypt(self):
        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "encrypt": True
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "encrypt": True,
                                      "public_key": "not a public key"
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "encrypt": True,
                                      "public_key": """-----BEGIN PUBLIC KEY-----
                                                       MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                                                       MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                                                       sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                                                       DoNemKEpyCt2dZTaQwIDAQAB
                                                       -----END PUBLIC KEY-----""",
                                      "random_string": "1234567891%Y%m%d",
                                      "random_string_date_field": "date"
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "encrypt": True,
                                      "public_key": """-----BEGIN PUBLIC KEY-----
                                                       MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                                                       MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                                                       sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                                                       DoNemKEpyCt2dZTaQwIDAQAB
                                                       -----END PUBLIC KEY-----""",
                                      "random_string_date_field": "date",
                                      "random_string_date_format": "%Y-%m-%d %H:%M:%S",
                                      "random_string": "1234567891"
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "encrypt": True,
                                      "random_string": "A" * 18 + "%Y",
                                      "random_string_date_field": "date",
                                      "random_string_date_format": "%Y-%m-%d %H:%M:%S",
                                      "public_key": """-----BEGIN PUBLIC KEY-----
                                                       MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                                                       MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                                                       sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                                                       DoNemKEpyCt2dZTaQwIDAQAB
                                                       -----END PUBLIC KEY-----"""
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "encrypt": True,
                                      "public_key": """-----BEGIN PUBLIC KEY-----
                                                       MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                                                       MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                                                       sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                                                       DoNemKEpyCt2dZTaQwIDAQAB
                                                       -----END PUBLIC KEY-----""",
                                      "random_string_date_field": "date_not_there",
                                      "random_string_date_format": "%Y-%m-%d %H:%M:%S",
                                      "random_string": "1234567891%y%m%d"
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

    def test_errors_decrypt(self):
        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "decrypt": True
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "from",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "decrypt": True,
                                      "private_key": "not a private key"
                                  }}]
                          },
                          expected_error=ScrubberValidationError)

    def test_email_base(self):
        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "to",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record"
                                  }},
                                  {
                                      "rule_type": "String",
                                      "field": "from",
                                      "params": {
                                          "minimum_length": 5,
                                          "maximum_length": 1024,
                                          "regex": "[^@]+@[^\\.]..*[^\\.]",
                                          "fallback_mode": "remove_record"
                                      }},
                                  {
                                      "rule_type": "Date",
                                      "field": "date",
                                      "params": {
                                          "date_format": "%Y-%m-%d %H:%M:%S",
                                          "fallback_mode": "remove_record",
                                          "range_minimum": "1970-01-01 00:00:00",
                                          "range_maximum": "2100-01-01 00:00:00",
                                      }},
                                  {
                                      "rule_type": "String",
                                      "field": "subject",
                                      "params": {
                                          "minimum_length": 0,
                                          "maximum_length": 1024,
                                          "fallback_mode": "remove_record"
                                      }}]
                          },
                          report=[])

    def test_email_hash(self):
        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails_hash.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "to",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "hash": True,
                                      "salt": "A97ASFNKJ#&"
                                  }},
                                  {
                                      "rule_type": "String",
                                      "field": "from",
                                      "params": {
                                          "minimum_length": 5,
                                          "maximum_length": 1024,
                                          "regex": "[^@]+@[^\\.]..*[^\\.]",
                                          "fallback_mode": "remove_record",
                                          "hash": True,
                                          "salt": "A97ASFNKJ#&"
                                      }},
                                  {
                                      "rule_type": "Date",
                                      "field": "date",
                                      "params": {
                                          "date_format": "%Y-%m-%d %H:%M:%S",
                                          "fallback_mode": "remove_record",
                                          "range_minimum": "1970-01-01 00:00:00",
                                          "range_maximum": "2100-01-01 00:00:00",
                                      }},
                                  {
                                      "rule_type": "String",
                                      "field": "subject",
                                      "params": {
                                          "minimum_length": 0,
                                          "maximum_length": 1024,
                                          "fallback_mode": "remove_record"
                                      }}]
                          },
                          report=[
                              {

                                  'field': 'to_clean',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Hashed all values',
                                  'df': [['3088b61a1fb2b613'],
                                         ['754d2dc7563c36f1'],
                                         ['4b6c888fa57e29dd'],
                                         ['3088b61a1fb2b613'],
                                         ['754d2dc7563c36f1'],
                                         ['4b6c888fa57e29dd']],

                              },
                              {

                                  'field': 'from_clean',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Hashed all values',
                                  'df': [['754d2dc7563c36f1'],
                                         ['3088b61a1fb2b613'],
                                         ['3088b61a1fb2b613'],
                                         ['754d2dc7563c36f1'],
                                         ['3088b61a1fb2b613'],
                                         ['754d2dc7563c36f1']],

                              },
                          ])

    def test_email_hash_rotating(self):
        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails_rotating_hash.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "to",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "hash": True,
                                      "salt": "A9788@%y%m%d",
                                      "salt_date_field": "date",
                                      "salt_date_format": "%Y-%m-%d %H:%M:%S"
                                  }},
                                  {
                                      "rule_type": "String",
                                      "field": "from",
                                      "params": {
                                          "minimum_length": 5,
                                          "maximum_length": 1024,
                                          "regex": "[^@]+@[^\\.]..*[^\\.]",
                                          "fallback_mode": "remove_record",
                                          "hash": True,
                                          "salt": "A9788@%y%m%d",
                                          "salt_date_field": "date",
                                          "salt_date_format": "%Y-%m-%d %H:%M:%S"
                                      }},
                                  {
                                      "rule_type": "Date",
                                      "field": "date",
                                      "params": {
                                          "date_format": "%Y-%m-%d %H:%M:%S",
                                          "fallback_mode": "remove_record",
                                          "range_minimum": "1970-01-01 00:00:00",
                                          "range_maximum": "2100-01-01 00:00:00",
                                      }},
                                  {
                                      "rule_type": "String",
                                      "field": "subject",
                                      "params": {
                                          "minimum_length": 0,
                                          "maximum_length": 1024,
                                          "fallback_mode": "remove_record"
                                      }}]
                          },
                          report=[
                              {

                                  'field': 'to_clean',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Hashed all values to salt date',
                                  'df': [['1990-10-12 18:32:42', 'dc7a794b4d88ed33'],
                                         ['1990-10-12 18:35:42', '862fc7f148bdc155'],
                                         ['1990-10-12 18:37:22', '48d01575e5e1c26d'],
                                         ['1990-10-12 18:45:42', 'dc7a794b4d88ed33'],
                                         ['1990-10-13 08:23:11', '9b64a5446478edea'],
                                         ['1990-10-13 11:22:33', 'd13fdff7bc26425c']],

                              },
                              {

                                  'field': 'from_clean',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Hashed all values to salt date',
                                  'df': [['1990-10-12 18:32:42', '862fc7f148bdc155'],
                                         ['1990-10-12 18:35:42', 'dc7a794b4d88ed33'],
                                         ['1990-10-12 18:37:22', 'dc7a794b4d88ed33'],
                                         ['1990-10-12 18:45:42', '862fc7f148bdc155'],
                                         ['1990-10-13 08:23:11', 'e640150619112ae9'],
                                         ['1990-10-13 11:22:33', '9b64a5446478edea']],

                              },
                          ])

    def test_email_encryption(self):
        df_1 = [[
            'upbFgaZ1gIbH8ph7uY8LFTCHG/yzPBxKwIguiHW/0TwK3I46QLZJwWj/YdB9kQ04RDuSUEm5+'
            'J5sti4hwZbSFU4WUAylZn82kw+dGSSUqPpSjn+MwQE58zTUUVULzBX0oceY5psr2Aur3EbzTulLxWKkkx73HcsFHDhKD6qdx84='],
            [
                'OGoDXfksvrNzCz09u1dGZcYY1gNWLMIZAdb32l+mJPrY7KeXDQkJ7NnE42Q2AtbV0r76yrHThP7E2Wj'
                '9hUc8Fgx3cgOPMxHnXnDNFcZL1wrk0WmpIqaDUtFG8a2/fzpfi4RWG9l/F6jUn7Kat4WQpa0UHVgxL21gTTGAnStZqyU='],
            [
                'SukuZeemYwKNV1trdUbAoGtODop3RvU4EKNXUVR/oonm7uu+fiqdSsPYrXiVHztfXQbZrFz69Gt0LfHwU7VqmSg4uMg'
                'K8/sqQaHUSDUxPtY2AEB7M1EsqrdsnzvDZzf87E/R7JC+ZYW7kAZXpjHWE5LA0nZH/j6o4r+jlRFvxX8='],
            [
                'upbFgaZ1gIbH8ph7uY8LFTCHG/yzPBxKwIguiHW/0TwK3I46QLZJwWj/YdB9kQ04RDuSUEm5+J5sti4hwZbSFU4WUAyl'
                'Zn82kw+dGSSUqPpSjn+MwQE58zTUUVULzBX0oceY5psr2Aur3EbzTulLxWKkkx73HcsFHDhKD6qdx84='],
            [
                'OGoDXfksvrNzCz09u1dGZcYY1gNWLMIZAdb32l+mJPrY7KeXDQkJ7NnE42Q2AtbV0r76yrHThP7E2Wj9hUc8'
                'Fgx3cgOPMxHnXnDNFcZL1wrk0WmpIqaDUtFG8a2/fzpfi4RWG9l/F6jUn7Kat4WQpa0UHVgxL21gTTGAnStZqyU='],
            [
                'SukuZeemYwKNV1trdUbAoGtODop3RvU4EKNXUVR/oonm7uu+fiqdSsPYrXiVHztfXQbZrFz69Gt0LfHwU7VqmSg4uMgK8'
                '/sqQaHUSDUxPtY2AEB7M1EsqrdsnzvDZzf87E/R7JC+ZYW7kAZXpjHWE5LA0nZH/j6o4r+jlRFvxX8=']]

        df_2 = [[
            'OGoDXfksvrNzCz09u1dGZcYY1gNWLMIZAdb32l+mJPrY7KeXDQkJ7NnE42Q2AtbV0r76yrHThP7E2Wj9hUc8F'
            'gx3cgOPMxHnXnDNFcZL1wrk0WmpIqaDUtFG8a2/fzpfi4RWG9l'
            '/F6jUn7Kat4WQpa0UHVgxL21gTTGAnStZqyU='],
            [
                'upbFgaZ1gIbH8ph7uY8LFTCHG/yzPBxKwIguiHW/0TwK3I46QLZJwWj/YdB9kQ04RDuSUEm5+J5sti4hwZbSFU4WUAylZn82kw+'
                'dGSSUqPpSjn+MwQE58zTUUVULzBX0oceY5psr2Aur3EbzTulLxWKkkx73HcsFHDhKD6qdx84='],
            [
                'upbFgaZ1gIbH8ph7uY8LFTCHG/yzPBxKwIguiHW/0TwK3I46QLZJwWj/YdB9kQ04RDuSUEm5+J5sti4hwZbSFU4WUAylZn82kw+d'
                'GSSUqPpSjn+MwQE58zTUUVULzBX0oceY5psr2Aur3EbzTulLxWKkkx73HcsFHDhKD6qdx84='],
            [
                'OGoDXfksvrNzCz09u1dGZcYY1gNWLMIZAdb32l+mJPrY7KeXDQkJ7NnE42Q2AtbV0r76yrHThP7E2Wj9hUc8F'
                'gx3cgOPMxHnXnDNFcZL1wrk0WmpIqaDUtFG8a2/fzpfi4RWG9l/F6jUn7Kat4WQpa0UHVgxL21gTTGAnStZqyU='],
            [
                'upbFgaZ1gIbH8ph7uY8LFTCHG/yzPBxKwIguiHW/0TwK3I46QLZJwWj/YdB9kQ04RDuSUEm5+J5sti4hwZbSFU4WUAylZn82kw+'
                'dGSSUqPpSjn+MwQE58zTUUVULzBX0oceY5psr2Aur3EbzTulLxWKkkx73HcsFHDhKD6qdx84='],
            [
                'OGoDXfksvrNzCz09u1dGZcYY1gNWLMIZAdb32l+mJPrY7KeXDQkJ7NnE42Q2AtbV0r76yrHThP7E2Wj9hUc8F'
                'gx3cgOPMxHnXnDNFcZL1wrk0WmpIqaDUtFG8a2/fzpfi4RWG9l/F6jUn7Kat4WQpa0UHVgxL21gTTGAnStZqyU=']]

        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails_encrypted.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "to",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "encrypt": True,
                                      "random_string": "",
                                      "public_key": """-----BEGIN PUBLIC KEY-----
                               MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                               MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                               sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                               DoNemKEpyCt2dZTaQwIDAQAB
                               -----END PUBLIC KEY-----"""
                                  }},
                                  {
                                      "rule_type": "String",
                                      "field": "from",
                                      "params": {
                                          "minimum_length": 5,
                                          "maximum_length": 1024,
                                          "regex": "[^@]+@[^\\.]..*[^\\.]",
                                          "fallback_mode": "remove_record",
                                          "encrypt": True,
                                          "random_string": "",
                                          "public_key": """-----BEGIN PUBLIC KEY-----
                               MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                               MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                               sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                               DoNemKEpyCt2dZTaQwIDAQAB
                               -----END PUBLIC KEY-----"""
                                      }},
                                  {
                                      "rule_type": "Date",
                                      "field": "date",
                                      "params": {
                                          "date_format": "%Y-%m-%d %H:%M:%S",
                                          "fallback_mode": "remove_record",
                                          "range_minimum": "1970-01-01 00:00:00",
                                          "range_maximum": "2100-01-01 00:00:00",
                                      }},
                                  {
                                      "rule_type": "String",
                                      "field": "subject",
                                      "params": {
                                          "minimum_length": 0,
                                          "maximum_length": 1024,
                                          "fallback_mode": "remove_record"
                                      }}]
                          },
                          report=[
                              {

                                  'field': 'to_clean',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Encrypted values',
                                  'df': df_1,

                              },
                              {

                                  'field': 'from_clean',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Encrypted values',
                                  'df': df_2,

                              },
                          ])

    def test_email_encryption_rotating(self):
        df_1 = [[
            'm8M0AWJgi3a0ntCDQMTCoMrAa9WbM9qW1soucDTMzXEa/gnHLSiEaTZ+x1mi4bag7JaRNOYJsXBQDTOwEHh+CjvkF/nNK'
            '+y7ViboXCWHhi9UpF7HePBCFpNtHATguIQQrQzvHq3wYPXax58u6tQrxrCXVDfBt7+pCpUODwz6KP4=',
            '1990-10-12 18:32:42'],
            [
                'Y0pS5yTkR7iXTnp6ZbnRxTI0aEWPJoFjb8we6aasooXoK3/GOsmmaGt6pBnN6GUFUCMly+iOMjX5veW340Xp'
                '+f6o783RPCMiaroYJPMgenu4w3b8SZWP4YH0Nled3Lmn6a/iBuwDNyUydQ0dmKCRxoU8YGqQ8bE8MXf+Ot38P7w=',
                '1990-10-12 18:35:42'],
            [
                'iBlLHVl9PlncLgbtbRAZJix/q005QWlOTBhrYVZhBtG5wRy1gwX1DqZ2bSf1pxFhBggrxAlwKyOFO04t3qBrtqZwpKRK1oCb'
                '+z45WDSc7Cdvi5MwgmH5EG34gOxcI3Ms36KsZ5m35VwXHU8B8t3JucipQcHlwA+CdzGdBmRHKeo=',
                '1990-10-12 18:37:22'],
            [
                'm8M0AWJgi3a0ntCDQMTCoMrAa9WbM9qW1soucDTMzXEa/gnHLSiEaTZ+x1mi4bag7JaRNOYJsXBQDTOwEHh+CjvkF/nNK'
                '+y7ViboXCWHhi9UpF7HePBCFpNtHATguIQQrQzvHq3wYPXax58u6tQrxrCXVDfBt7+pCpUODwz6KP4=',
                '1990-10-12 18:45:42'],
            [
                'If5mhgQMGFQCNxG5i5anZ0VndyfGAXHKgv3hBmmIbrYFvRB6USKGBeoOGnngRER1kydAdN52i4jJOG4Q6qKsuDAayn9M'
                '/DkNLLIsqJ0GXcndQYDz9e17ExsJJ4ZxVpVhvEZSSGLzIUNNH9dssNZ8Huz/ERFNGKA+ENdTsR/fm7A=',
                '1990-10-13 08:23:11'],
            [
                'YBtY8GvdTlUOxzdFxatzeHu8Ze3LPGcDueLqbPd6yK9iGibgjI/oTay/MQgPH8ybAwQ50Uv4/HxnjwTfPZTbzSXsJ'
                '+YPIjkZAFyDK4pjUepFKWdGESiQ/6OCt4MuPPN5dwk4KDHcdhrgabN7cesBP1X5+QveierexMjDtMGValo=',
                '1990-10-13 11:22:33']]

        df_2 = [[
            'Y0pS5yTkR7iXTnp6ZbnRxTI0aEWPJoFjb8we6aasooXoK3/GOsmmaGt6pBnN6GUFUCMly+iOMjX5veW340Xp'
            '+f6o783RPCMiaroYJPMgenu4w3b8SZWP4YH0Nled3Lmn6a/iBuwDNyUydQ0dmKCRxoU8YGqQ8bE8MXf+Ot38P7w=',
            '1990-10-12 18:32:42'],
            [
                'm8M0AWJgi3a0ntCDQMTCoMrAa9WbM9qW1soucDTMzXEa/gnHLSiEaTZ+x1mi4bag7JaRNOYJsXBQDTOwEHh+CjvkF/nNK'
                '+y7ViboXCWHhi9UpF7HePBCFpNtHATguIQQrQzvHq3wYPXax58u6tQrxrCXVDfBt7+pCpUODwz6KP4=',
                '1990-10-12 18:35:42'],
            [
                'm8M0AWJgi3a0ntCDQMTCoMrAa9WbM9qW1soucDTMzXEa/gnHLSiEaTZ+x1mi4bag7JaRNOYJsXBQDTOwEHh+CjvkF/nNK'
                '+y7ViboXCWHhi9UpF7HePBCFpNtHATguIQQrQzvHq3wYPXax58u6tQrxrCXVDfBt7+pCpUODwz6KP4=',
                '1990-10-12 18:37:22'],
            [
                'Y0pS5yTkR7iXTnp6ZbnRxTI0aEWPJoFjb8we6aasooXoK3/GOsmmaGt6pBnN6GUFUCMly+iOMjX5veW340Xp'
                '+f6o783RPCMiaroYJPMgenu4w3b8SZWP4YH0Nled3Lmn6a/iBuwDNyUydQ0dmKCRxoU8YGqQ8bE8MXf+Ot38P7w=',
                '1990-10-12 18:45:42'],
            [
                'Zypg4OEJFFik9fAB/SujORdjIagGlZcksn/+eTPeHm5IdTOIWm77aa/ij+3H5lqQEz1LoVWst8V5TtGJ/gMq63fAYsoj3pN'
                '+vNIM1lKpGrybO1JagDsPHP2o6GESjUrFKrfkH2OzdWDchHCdDksx8b/eMtOI8oTakncaZMwcPYA=',
                '1990-10-13 08:23:11'],
            [
                'If5mhgQMGFQCNxG5i5anZ0VndyfGAXHKgv3hBmmIbrYFvRB6USKGBeoOGnngRER1kydAdN52i4jJOG4Q6qKsuDAayn9M'
                '/DkNLLIsqJ0GXcndQYDz9e17ExsJJ4ZxVpVhvEZSSGLzIUNNH9dssNZ8Huz/ERFNGKA+ENdTsR/fm7A=',
                '1990-10-13 11:22:33']]
        self._test_filter(dirty_file="anonymization/emails.csv",
                          clean_file="anonymization/emails_rotating_encrypted.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "to",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "encrypt": True,
                                      "public_key": """-----BEGIN PUBLIC KEY-----
                               MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                               MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                               sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                               DoNemKEpyCt2dZTaQwIDAQAB
                               -----END PUBLIC KEY-----""",
                                      "random_string": "A9788@%y%m%d",
                                      "random_string_date_field": "date",
                                      "random_string_date_format": "%Y-%m-%d %H:%M:%S"
                                  }},
                                  {
                                      "rule_type": "String",
                                      "field": "from",
                                      "params": {
                                          "minimum_length": 5,
                                          "maximum_length": 1024,
                                          "regex": "[^@]+@[^\\.]..*[^\\.]",
                                          "fallback_mode": "remove_record",
                                          "encrypt": True,
                                          "public_key": """-----BEGIN PUBLIC KEY-----
                               MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                               MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                               sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                               DoNemKEpyCt2dZTaQwIDAQAB
                               -----END PUBLIC KEY-----""",
                                          "random_string": "A9788@%y%m%d",
                                          "random_string_date_field": "date",
                                          "random_string_date_format": "%Y-%m-%d %H:%M:%S"
                                      }},
                                  {
                                      "rule_type": "Date",
                                      "field": "date",
                                      "params": {
                                          "date_format": "%Y-%m-%d %H:%M:%S",
                                          "fallback_mode": "remove_record",
                                          "range_minimum": "1970-01-01 00:00:00",
                                          "range_maximum": "2100-01-01 00:00:00",
                                      }},
                                  {
                                      "rule_type": "String",
                                      "field": "subject",
                                      "params": {
                                          "minimum_length": 0,
                                          "maximum_length": 1024,
                                          "fallback_mode": "remove_record"
                                      }}]
                          },
                          report=[
                              {

                                  'field': 'to_clean',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Encrypted values to date field',
                                  'df': df_1,

                              },
                              {

                                  'field': 'from_clean',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Encrypted values to date field',
                                  'df': df_2,

                              },
                          ])

    def test_email_decryption(self):
        self._test_filter(dirty_file="anonymization/emails_rotating_encrypted.csv",
                          clean_file="anonymization/emails.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "to",
                                  "params": {
                                      "minimum_length": 5,
                                      "maximum_length": 1024,
                                      "regex": "[^@]+@[^\\.]..*[^\\.]",
                                      "fallback_mode": "remove_record",
                                      "decrypt": True,
                                      "private_key": """-----BEGIN RSA PRIVATE KEY-----
                                MIICXQIBAAKBgQDDmPPm5UC8rXn4uX37m4tN/j4TMAhUVyxN7V7QxMF3HDg5rkl/
                                Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10sZI0kIrkizlKaB/20Q4P1kYO
                                Cgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0DoNemKEpyCt2dZTaQwIDAQAB
                                AoGBAIxvLv8irp5JN3+7Ppb+EMDIwCzqmbBkfmzc9uyRuA4a9suDNUXT3/ceFoyF
                                QpFPGb/i2YlfRLGzjVxjE5/WET9bf//ATOkZyn2sl4jBGs9WIF4by+246E+dfol9
                                /326rSpJjVeklmELU3nJp4ViZzYX+Cwc0rucpZLMqLUUFbvhAkEAzP+WSV2cp5w4
                                E1OBDM7cyq3lneWP0N1OdteZPZlJT0ojsQuoggqvcUMeC/eSoaHyZGN7GS4OVtaC
                                BR++kkPiCwJBAPRCnk4FmeLtnDpTX7KV8a766jSqkDzqEKVVqoGfLYCe0uaWFcwK
                                MKBik0GJ6tFLg9JvJMbP1+eD8+2uQD7rg6kCQDNghyDiBkX3oBIv5nL4UVu2k4qs
                                IwwcuvKL/Er05OurUCCqJFRbKzc+tAQZyzUZKm/AgvR/l3ZqEnIIT7HGs5sCQDej
                                NQvwmqzmEr/2XcYAAZ0p6k80ysYVStVePghoiaTSiJedeDmR2KGv0nsLP0GNQemd
                                B3OBxFwn4lgxaNDsNIECQQCTrHWrS/v5rh5sNNPC8dn7e4TThuvQ5l/mv5zTZHu9
                                rtdkt0kn4xawfR5p0nrW6HL2M3pRbJ0obi6h//HZc8KX
                                -----END RSA PRIVATE KEY-----"""
                                  }},
                                  {
                                      "rule_type": "String",
                                      "field": "from",
                                      "params": {
                                          "minimum_length": 5,
                                          "maximum_length": 1024,
                                          "regex": "[^@]+@[^\\.]..*[^\\.]",
                                          "fallback_mode": "remove_record",
                                          "decrypt": True,
                                          "private_key": """-----BEGIN RSA PRIVATE KEY-----
                                MIICXQIBAAKBgQDDmPPm5UC8rXn4uX37m4tN/j4TMAhUVyxN7V7QxMF3HDg5rkl/
                                Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10sZI0kIrkizlKaB/20Q4P1kYO
                                Cgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0DoNemKEpyCt2dZTaQwIDAQAB
                                AoGBAIxvLv8irp5JN3+7Ppb+EMDIwCzqmbBkfmzc9uyRuA4a9suDNUXT3/ceFoyF
                                QpFPGb/i2YlfRLGzjVxjE5/WET9bf//ATOkZyn2sl4jBGs9WIF4by+246E+dfol9
                                /326rSpJjVeklmELU3nJp4ViZzYX+Cwc0rucpZLMqLUUFbvhAkEAzP+WSV2cp5w4
                                E1OBDM7cyq3lneWP0N1OdteZPZlJT0ojsQuoggqvcUMeC/eSoaHyZGN7GS4OVtaC
                                BR++kkPiCwJBAPRCnk4FmeLtnDpTX7KV8a766jSqkDzqEKVVqoGfLYCe0uaWFcwK
                                MKBik0GJ6tFLg9JvJMbP1+eD8+2uQD7rg6kCQDNghyDiBkX3oBIv5nL4UVu2k4qs
                                IwwcuvKL/Er05OurUCCqJFRbKzc+tAQZyzUZKm/AgvR/l3ZqEnIIT7HGs5sCQDej
                                NQvwmqzmEr/2XcYAAZ0p6k80ysYVStVePghoiaTSiJedeDmR2KGv0nsLP0GNQemd
                                B3OBxFwn4lgxaNDsNIECQQCTrHWrS/v5rh5sNNPC8dn7e4TThuvQ5l/mv5zTZHu9
                                rtdkt0kn4xawfR5p0nrW6HL2M3pRbJ0obi6h//HZc8KX
                                -----END RSA PRIVATE KEY-----"""
                                      }},
                                  {
                                      "rule_type": "Date",
                                      "field": "date",
                                      "params": {
                                          "date_format": "%Y-%m-%d %H:%M:%S",
                                          "fallback_mode": "remove_record",
                                          "range_minimum": "1970-01-01 00:00:00",
                                          "range_maximum": "2100-01-01 00:00:00",
                                      }},
                                  {
                                      "rule_type": "String",
                                      "field": "subject",
                                      "params": {
                                          "minimum_length": 0,
                                          "maximum_length": 1024,
                                          "fallback_mode": "remove_record"
                                      }}]
                          },
                          report=[
                              {

                                  'field': 'to',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Decrypted all values',
                                  'df': [['steve@apple.com'],
                                         ['wos@apple.com'],
                                         ['billg@microsoft.com'],
                                         ['steve@apple.com'],
                                         ['wos@apple.com'],
                                         ['billg@microsoft.com']],

                              },
                              {

                                  'field': 'from',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'modified',
                                  'description': 'Decrypted all values',
                                  'df': [['wos@apple.com'],
                                         ['steve@apple.com'],
                                         ['steve@apple.com'],
                                         ['wos@apple.com'],
                                         ['steve@apple.com'],
                                         ['wos@apple.com']],

                              },
                          ])

    def test_email_encryption_inconsistent(self):
        csv = CSVHandler(base_path=self.base_path)

        df = csv.get_dataframe("anonymization/emails.csv")

        scrubber = Scrubber()

        scrubber.run(df=df,
                     config={"rules": [
                         {
                             "rule_type": "String",
                             "field": "to",
                             "params": {
                                 "minimum_length": 5,
                                 "maximum_length": 1024,
                                 "regex": "[^@]+@[^\\.]..*[^\\.]",
                                 "fallback_mode": "remove_record",
                                 "encrypt": True,
                                 "public_key": """-----BEGIN PUBLIC KEY-----
                           MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                           MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                           sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                           DoNemKEpyCt2dZTaQwIDAQAB
                           -----END PUBLIC KEY-----"""
                             }}]})

        scrubber.run(df=df,
                     config={"rules": [
                         {
                             "rule_type": "String",
                             "field": "to",
                             "params": {
                                 "minimum_length": 5,
                                 "maximum_length": 1024,
                                 "regex": "[^@]+@[^\\.]..*[^\\.]",
                                 "fallback_mode": "remove_record",
                                 "decrypt": True,
                                 "private_key": """-----BEGIN RSA PRIVATE KEY-----
                            MIICXQIBAAKBgQDDmPPm5UC8rXn4uX37m4tN/j4TMAhUVyxN7V7QxMF3HDg5rkl/
                            Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10sZI0kIrkizlKaB/20Q4P1kYO
                            Cgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0DoNemKEpyCt2dZTaQwIDAQAB
                            AoGBAIxvLv8irp5JN3+7Ppb+EMDIwCzqmbBkfmzc9uyRuA4a9suDNUXT3/ceFoyF
                            QpFPGb/i2YlfRLGzjVxjE5/WET9bf//ATOkZyn2sl4jBGs9WIF4by+246E+dfol9
                            /326rSpJjVeklmELU3nJp4ViZzYX+Cwc0rucpZLMqLUUFbvhAkEAzP+WSV2cp5w4
                            E1OBDM7cyq3lneWP0N1OdteZPZlJT0ojsQuoggqvcUMeC/eSoaHyZGN7GS4OVtaC
                            BR++kkPiCwJBAPRCnk4FmeLtnDpTX7KV8a766jSqkDzqEKVVqoGfLYCe0uaWFcwK
                            MKBik0GJ6tFLg9JvJMbP1+eD8+2uQD7rg6kCQDNghyDiBkX3oBIv5nL4UVu2k4qs
                            IwwcuvKL/Er05OurUCCqJFRbKzc+tAQZyzUZKm/AgvR/l3ZqEnIIT7HGs5sCQDej
                            NQvwmqzmEr/2XcYAAZ0p6k80ysYVStVePghoiaTSiJedeDmR2KGv0nsLP0GNQemd
                            B3OBxFwn4lgxaNDsNIECQQCTrHWrS/v5rh5sNNPC8dn7e4TThuvQ5l/mv5zTZHu9
                            rtdkt0kn4xawfR5p0nrW6HL2M3pRbJ0obi6h//HZc8KX
                            -----END RSA PRIVATE KEY-----"""
                             }}]})

        self._compare_df_to_file(csv, df, "anonymization/emails.csv")
