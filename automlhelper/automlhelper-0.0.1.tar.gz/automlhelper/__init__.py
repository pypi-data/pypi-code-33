from automlhelper.storageio import StorageIO
from automlhelper.automl import AutoML

class AutoMLHelper:

    def __init__(self, bucket_name, csv_path, project_name):
        self.bucket_name = bucket_name
        self.csv_path = csv_path
        self.project_name = project_name
        self.automl = AutoML(project_name)
        self.storageio = StorageIO(bucket_name, csv_path)
        self.performance = False
        self.tags = False

    def tag_performance(self):
        if self.performance == False:
            self.performance = self.automl.get_tag_evaluation()

        if self.tags == False:
            self.tags = sorted(self.get_tags(),reverse=True)
        
        return zip(self.tags, self.performance)
    
    def tag_and_performance(self, key='base_au_prc'):
        values = []
        for t,p in self.tag_performance():
            values.append((t, getattr(p.classification_evaluation_metrics, key)))
        return values

    def best_performing(self, key='base_au_prc', limit=0, reverse=True): 
        values = sorted(self.tag_and_performance(key), key=lambda _: _[1], reverse=reverse)
        
        if limit > 0:
            return values[0:limit]
        else:
            return values

    def get_tags(self):
        lines = self.storageio.get_csv_lines()
        tags = []
        for l in lines:
            for t in l.split(','):
                if 'gs://' not in t and t not in tags + ['TRAIN','TEST','VALIDATION']:
                    tags.append(t)

        return sorted(tags)

    def get_examples_of(self, tag_name, limit=10):
        csv_lines = self.storageio.get_csv_lines()
        files = []

        for line in csv_lines:
            if len(files) > limit:
                break
            
            breaks = line.split(',')

            if tag_name in breaks:
                gs_file = list(filter(lambda _: 'gs://' in _,breaks))[0]
                files.append(self.storageio.gs_to_link(gs_file))
        return files

    def predict_gs(self, gs_file):
        return self.automl.get_predictions(
            self.storageio.get_base64_from_gs(gs_file)
        )