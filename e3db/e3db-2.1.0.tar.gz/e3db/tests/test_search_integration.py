import e3db
import os
import binascii
import pytest
import time
import e3db.types
import hashlib
import requests
from datetime import datetime
from datetime import timedelta
from ..auth import E3DBAuth
from ..types import ClientDetails

api_url = os.environ["DEFAULT_API_URL"]
token = os.environ["REGISTRATION_TOKEN"]
### Variables required for internal testing
local_api_url = os.environ["LOCAL_API_URL"]
local_boot_key = os.environ["LOCAL_BOOT_KEY"]
local_boot_secret = os.environ["LOCAL_BOOT_SECRET"]
local_register = os.environ["USE_LOCAL_REGISTER"]

class TestSearchIntegration():
    @classmethod
    def register_client(self):
        client1_public_key, client1_private_key = e3db.Client.generate_keypair()
        client1_name = "email_{0}@tozny.com".format(time.time())
        test_client1 = e3db.Client.register(token, client1_name, client1_public_key, api_url=api_url)
        client1_api_key_id = test_client1.api_key_id
        client1_api_secret = test_client1.api_secret
        client1_id = test_client1.client_id

        client1_config = e3db.Config(
            client1_id,
            client1_api_key_id,
            client1_api_secret,
            client1_public_key,
            client1_private_key,
            api_url=api_url 
        )
        self.client1 = e3db.Client(client1_config())

        client2_public_key, client2_private_key = e3db.Client.generate_keypair()
        client2_name = "email_{0}@tozny.com".format(time.time())
        test_client2 = e3db.Client.register(token, client2_name, client2_public_key, api_url=api_url)
        client2_api_key_id = test_client2.api_key_id
        client2_api_secret = test_client2.api_secret
        client2_id = test_client2.client_id

        client2_config = e3db.Config(
            client2_id,
            client2_api_key_id,
            client2_api_secret,
            client2_public_key,
            client2_private_key,
            api_url=api_url 
        )
        self.client2 = e3db.Client(client2_config())

    @classmethod
    def internal_register_client(self):
        """
        Method for local testing only
        """
        client1_public_key, client1_private_key = e3db.Client.generate_keypair()

        url = "{0}/{1}/{2}/{3}".format(local_api_url, 'v1', 'storage', 'clients')
        email = "email_{0}@tozny.com".format(time.time())
        payload = {
            'email': email,
            'public_key': {
                'curve25519': client1_public_key
            },
            'private_key': {
                'curve25519': client1_private_key
            }
        }
        bootstrapAuth = E3DBAuth(local_boot_key, local_boot_secret, local_api_url)
        response = requests.post(url=url, json=payload, auth=bootstrapAuth)
        client_info = response.json()

        client1_config = e3db.Config(
            client_info["client_id"],
            client_info["api_key_id"],
            client_info["api_secret"],
            client1_public_key,
            client1_private_key,
            api_url=local_api_url 
        )
        self.client1 = e3db.Client(client1_config())

    @classmethod
    def wait_for_index_record(self, retries):
        """
        Instead of sleeping, delay tests until the latest record is found.
        """
        found = False
        wait = 1 
        record_id = self.encrypted_file_meta.record_id
        while not found and retries >= 0:
            q = e3db.types.Search().match(records=[record_id])
            results = self.client2.search(q)
            if len(results) != 1:
                time.sleep(wait)
                wait <<= 1 # double the time waited
                retries -= 1
            else:
                return True
        return False

    @classmethod
    def __help_create_large_file(self, fileName):
        with open(fileName, "wb+") as f:
            for _ in range(1, 1024):
                f.write(b'b' * 1024)
        return os.path.isfile(fileName)

    @classmethod
    def setup_class(self):
        if local_register == "true":
            self.internal_register_client()
        else:
            self.register_client()
        self.record_type = "SDK_integration_tests"
        self.record1 = self.client1.write(self.record_type, 
                                            {'time': str(time.time())}, 
                                            {'hello':'toznians',
                                            'regexp':'toznywebsite',
                                            'fuzzy':'veryveryfuzzy'
                                            })

        self.record2 = self.client1.write(self.record_type, 
                                            {'time': str(time.time())})
        self.pag_record_type = "page_record_test"
        self.pag_rec1 = self.client2.write(self.pag_record_type,
                                            {'time': str(time.time())})
        self.pag_rec2 = self.client2.write(self.pag_record_type,
                                            {'time': str(time.time())})
        self.pag_rec3 = self.client2.write(self.pag_record_type,
                                            {'time': str(time.time())})
        self.pag_rec4 = self.client2.write(self.pag_record_type,
                                            {'time': str(time.time())})
        self.pag_rec5 = self.client2.write(self.pag_record_type,
                                            {'time': str(time.time())})
        fileName = "large_file.txt"
        didCreate = self.__help_create_large_file(fileName)
        if not didCreate:
            pytest.exit("could not create large_file.txt")
        self.large_record_type = "large_files"
        self.encrypted_file_meta = self.client2.write_file(self.large_record_type, fileName, {"large":"test"})
        if not self.wait_for_index_record(retries=5):
            pytest.exit("Timeout while waiting for indexed record")

    def test_v2_search_write_and_query(self):
        record1_id = self.record1.meta.record_id
        q = e3db.types.Search(include_data=True).match(records=[record1_id])
        results = self.client1.search(q)
        for r in results:
            print("record:")
            print(r.to_json())
        assert(len(results) == 1)

    def test_v2_search_returns_nothing(self):
        q = e3db.types.Search(include_data=True).match(values=["ladsfkjadsklfjgarbagefdjsklafjkdljsaf"])
        results = self.client1.search(q)
        for r in results:
            print("record:")
            print(r.to_json())
        assert(len(results) == 0)

    def test_v2_other_client_finds_nothing(self):
        q = e3db.types.Search(count=1000).match(record_types=[self.record_type]).exclude(records=[self.record1.meta.record_id])
        results = self.client1.search(q)
        assert(len(results)==1)

        q = e3db.types.Search().match(record_types=[self.record_type])
        results = self.client2.search(q)
        assert(len(results)==0)

    def test_v2_search_fuzzy(self):
        q = e3db.types.Search(include_data=True, count=1000).match(strategy="FUZZY",values=["veryveryfunny"])
        results = self.client1.search(q)
        assert(len(results)==1)

    def test_v2_invalid_range(self):
        q = e3db.types.Search(include_data=True).match(record_types=[self.record_type]).range(start=datetime.now(), end=datetime.now())
        results = self.client1.search(q)
        assert(len(results)==0)

    def test_v2_valid_range(self):
        q = e3db.types.Search(include_data=True).match(record_types=[self.record_type]).range(zone="PST", start=datetime.now()+timedelta(hours=-1), end=datetime.now()+timedelta(hours=1))
        results = self.client1.search(q)
        assert(len(results)==2)

    def test_v2_multi_match(self):
        record1_id = self.record1.meta.record_id
        record2_id = self.record2.meta.record_id
        q = e3db.types.Search().match(records=[record1_id]).match(records=[record2_id])
        results = self.client1.search(q)
        assert(len(results)==2)

    def test_v2_multi_and_match(self):
        record1_id = self.record1.meta.record_id
        record2_id = self.record2.meta.record_id
        q = e3db.types.Search().match(condition="AND", records=[record1_id, record2_id])
        results = self.client1.search(q)
        assert(len(results)==0)

    def test_v2_receive_data(self):
        record1_id = self.record1.meta.record_id
        q = e3db.types.Search(include_data=True).match(records=[record1_id])
        results = self.client1.search(q)
        assert(len(results)==1)
        for r in results:
            assert(r.data is not None)

        q = e3db.types.Search(include_data=False).match(records=[record1_id])
        results = self.client1.search(q)
        assert(len(results)==1)
        for r in results:
            assert(r.data is None)

    def test_v2_search_regexp(self):
        q = e3db.types.Search(count=1000, include_data=True).match(strategy="REGEXP", values=['tozny.*'])
        results = self.client1.search(q)
        for r in results:
            print("record:")
            print(r.to_json())
        assert(len(results) == 1)
    
    def test_v1_file_meta(self):
        print("encrypted record id", self.encrypted_file_meta.record_id)
        results = self.client2.query(record=[self.encrypted_file_meta.record_id])
        assert(len(results) == 1)
        for r in results:
            print("returned", r.meta.to_json())
            print("expected", self.encrypted_file_meta.to_json())
            assert(r.data == {}) # Large Files come back with no Data
            assert(r.meta.file_meta is not None)
            assert(r.meta.file_meta._checksum == self.encrypted_file_meta.checksum)

    def test_v2_file_meta(self):
        q = e3db.types.Search().match(records=[self.encrypted_file_meta.record_id])
        results = self.client2.search(q)
        assert(len(results) == 1)
        for r in results:
            assert(r.meta.file_meta is not None)
            assert(r.meta.file_meta._checksum == self.encrypted_file_meta.checksum)

    def test_v2_pagination(self):
        q = e3db.types.Search(count=2).match(condition="AND", record_types=[self.pag_record_type], writers=[self.client2.client_id])
        results = self.client2.search(q)
        assert(len(results) == 2)
        assert(results.next_token == 2)
        assert(results.total_results == 5)

        q = e3db.types.Search(next_token=results.next_token, count=10).match(condition="AND", record_types=[self.pag_record_type], writers=[self.client2.client_id])
        results = self.client2.search(q)
        assert(len(results) == 3)
        assert(results.next_token == 0)
        assert(results.total_results == 5)