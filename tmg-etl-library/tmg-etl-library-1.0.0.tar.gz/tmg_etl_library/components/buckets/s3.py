from tmg_etl_library.components.buckets.bucket import Bucket


class S3Client(Bucket):
    def __init__(self, log):
        super().__init__(log)

    def upload_files(self):
        pass

    def download_files(self):
        pass

    def list_files(self):
        pass

    def delete_files(self):
        pass

    class S3File:
        pass
