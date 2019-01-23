import os
import sys


class BaseLoader(object):
    file_name = ""
    chunksize = 10000

    def __init__(self, root=".", conn=None, engine=None):
        self.root = root
        self.path = os.path.join(root, self.file_name)
        self.conn = conn
        self.engine = engine

    def validate_file_exists(self):
        if not os.path.exists(self.path):
            full_path = os.path.abspath(self.root)
            print("No `{}` file in the `{}` folder.".format(self.file_name, full_path))
            return False
        return True

    def pipeline(self):
        print("Running {} pipeline.".format(self.__class__.__name__))
        if not self.validate():
            return
        print("--> validated")
        data = self.load()
        print("--> loaded")
        transformed_data = self.pre_ingest_transform(data)
        print("--> transformed")
        print("--> ingesting data...")
        res = self.ingest(transformed_data)
        print("--> ingested")
        return res

    def validate(self):
        return self.validate_file_exists()

    def load(self):
        raise NotImplementedError()

    def pre_ingest_transform(self, data):
        return data

    def ingest(self, data):
        raise NotImplementedError()

    def inspect(self):
        return {}


class BaseMultiLoader(BaseLoader):
    file_names = []

    def __init__(self, root=".", conn=None, engine=None):
        self.root = root
        self.conn = conn
        self.engine = engine
        self.paths = [os.path.join(root, fn) for fn in self.file_names]

    def validate_file_exists(self):
        full_path = os.path.abspath(self.root)
        bad_files = 0
        for path in self.paths:
            if not os.path.exists(path):
                print(
                    "WARNING: Did not find `{}` file in the `{}` folder.".format(
                        path, full_path
                    )
                )
                bad_files += 1
        if bad_files == len(self.paths):
            print("Found no data, exiting.")
            return False
        return True
