
from collections import defaultdict

from airflow.models import BaseOperator


class AbstractOperator(BaseOperator):

    def execute(self, context):
        self._pre_execute(context)
        self._execute(context)
        self._post_execute(context)

    def _pre_execute(self, context):
        """ Pre execute logic. This method is executed before the main logic in the 'execute' method
            Default approach should exists here like get task_config """

        # get default params
        self.task_instance = context.get('task_instance', None)
        self.depends_on = context.get('depends_on', None)

        # get task config from default kwargs (for tests and mocks)
        self.task_config = context.get('task_config', None)

        # if not pass task_config, lets get from task instance
        if not self.task_config and self.depends_on:
            self.task_config = defaultdict(list)
            for config in self.task_instance.xcom_pull(task_ids=self.depends_on):
                if config and isinstance(config, dict):
                    for key, value in config.items():
                        self.task_config[key].append(value)

    def _execute(self, context):
        pass

    def _post_execute(self, context):
        pass