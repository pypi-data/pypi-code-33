# -*- coding: utf-8 -*-

import logging

from collections import defaultdict


class AbstractTask:

    log = logging.getLogger(__name__)

    depends_on = None
    task_instance = None

    task_config = None

    @classmethod
    def execute(cls, *args, **kwargs):
        cls._pre_execute(**kwargs)
        cls._execute(**kwargs)
        return cls._post_execute(**kwargs)

    @classmethod
    def check(cls, **kwargs):
        return True

    @classmethod
    def _pre_execute(cls, **kwargs):
        """ Pre execute logic. This method is executed before the main logic in the 'execute' method
            Default approach should exists here like get task_config """

        # get default params
        cls.task_instance = kwargs.get('task_instance', None)
        cls.depends_on = kwargs.get('depends_on', None)

        # get task config from default kwargs (for tests and mocks)
        cls.task_config = kwargs.get('task_config', None)

        # if not pass task_config, lets get from task instance
        if not cls.task_config and cls.depends_on:
            cls.task_config = defaultdict(list)
            for config in cls.task_instance.xcom_pull(task_ids=cls.depends_on):
                if config and isinstance(config, dict):
                    for key, value in config.items():
                        cls.task_config[key].append(value)

    @classmethod
    def _pre_validate(cls, **kwargs):
        """ Pre execute logic. This method is executed before the main logic in the 'execute' method """
        pass

    @classmethod
    def _execute(cls, **kwargs):
        """ Execute the main logic here """
        raise Exception('Not implemented! This method have implemented in child class!')

    @classmethod
    def _post_execute(cls, **kwargs):
        """ Post execute logic. This method is executed after the main logic in the 'execute' method """
        return True
