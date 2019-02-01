from cloud.bigquery_io import bigquery_io
from cloud.google_firebase import google_firebase
from cloud.universal_filemanager import universal_filemanager
from firebase_admin import firestore
from aether_shared.cloud.google_cloud_storage_io import google_cloud_storage_io

# from cloud.email_io import email_io


################################################################################################################
#
# A global object for all API Resources to access throughout their processing.
#
#
################################################################################################################

class api_global_objects(object):

    def __init__(self):
        self._authenticator = google_firebase()
        #self._email_client = email_io()
        self._cloud_storage_client = google_cloud_storage_io()
        self._bigquery_client = bigquery_io()
        self._filemanager = universal_filemanager(self._cloud_storage_client)

    def filemanager(self):
        return self._filemanager

    # def email_client(self):
    #     return self._email_client

    def cloud_storage_client(self):
        return self._cloud_storage_client

    def authenticator(self):
        return self._authenticator

    def bigquery_client(self):
        return self._bigquery_client

    def firestore_client(self):
        return self._authenticator.firestore_client()

    def firestore_module(self):
        return firestore
