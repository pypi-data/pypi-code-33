import os

if os.environ.get("DYNO") or os.environ.get("APPSETTING_WEBSITE_SITE_NAME") or os.environ.get("CUSTOM_MONGO_SERVER"):
    # if Heroku (DYNO), Azure (APPSETTING_WEBSITE_SITE_NAME) or custom env variable (CUSTOM_MONGO_SERVER)
    from pymongo import MongoClient as RealMongoClient

    class MongoClient(RealMongoClient):
        pass
else:
    from tinymongo import TinyMongoClient

    class MongoClient(TinyMongoClient):
        def __init__(self, host=None, port=None, document_class=dict, tz_aware=None, connect=None, **kwargs):
            if not host or "://" in host:  # if it's URL
                host = "localhost.db"

            super().__init__(foldername=host)
