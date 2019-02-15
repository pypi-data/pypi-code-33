# this task is chief if task_index = 0

class TrainingTask(object):
    def __init__(self, job_name, job_type, cluster_spec, task_index, model_location=None, dataset=None, requirement_location=None):
        assert job_name == "worker" or job_name == "ps"
        self.job_type = job_type
        self.task_index = task_index
        self.model_location = model_location
        self.dataset = dataset
        if job_name == "worker":
            assert(self.model_location is not None)
            assert (self.dataset is not None)

        self.job_name = job_name
        self.cluster_spec = cluster_spec
        self.requirement_location = requirement_location
