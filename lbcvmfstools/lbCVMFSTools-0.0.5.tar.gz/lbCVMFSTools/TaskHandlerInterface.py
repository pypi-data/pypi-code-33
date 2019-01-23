
class TaskHandlerInterface():

    def __init__(self, *args, **kwargs):
        if kwargs.get('dry_run', None):
            self.dry_run = kwargs['dry_run']
        else:
            self.dry_run = False

    def get_list_of_tasks(self):
        raise NotImplementedError()

    def preTransaction(self):
        raise NotImplementedError()

    def postTransaction(self):
        raise NotImplementedError()

    def perform_task(self, task):
        raise NotImplementedError()

    def configure(self):
        raise NotImplementedError()
