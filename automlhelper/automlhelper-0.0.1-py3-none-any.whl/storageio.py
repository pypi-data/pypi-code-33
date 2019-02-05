from google.cloud import storage
import base64

class StorageIO:

    def __init__(self, bucket_name, csv_path):
        self.csv_path = csv_path
        self.client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(self.bucket_name)
        self.csv_cache = {}
       
    def get_csv_lines(self):
        blobs = list(self.bucket.list_blobs(prefix=self.csv_path))
        csv_list = []
        for b in blobs:
            if 'csv' in b.name:
                csv_list.append(b)

        blob = sorted(csv_list, key=lambda _:_.name, reverse=True)[0]
        if blob.name not in self.csv_cache:
            self.csv_cache[blob.name] = blob.download_as_string()    
        return self.csv_cache[blob.name].decode("utf-8").split("\n")
    
    def get_base64_from_gs(self,gs_file):
        path = gs_file.replace(
            'gs://' + self.bucket_name + '/', ''
        ).replace(
            'https://storage.cloud.google.com/' + self.bucket_name + '/','')
        
        return self.bucket.blob(path).download_as_string()
        
        base64.b64encode(
            self.bucket.blob(path).download_as_string()
        )

    def gs_to_link(self, gs_file):
        return gs_file.replace('gs://', 'https://storage.cloud.google.com/')

    def link_to_gs(self, link):
        return link.replace('https://storage.cloud.google.com/', 'gs://')
