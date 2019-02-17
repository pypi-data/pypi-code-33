
import logging

from colibris import persist

from testmyesp import constants


class Client(persist.Model):
    id = persist.AutoField()
    name = persist.CharField(max_length=128, index=True, unique=True)
    secret = persist.CharField(max_length=128)
    role = persist.CharField(max_length=16)

    def __str__(self):
        return self.name


class Job(persist.Model):
    id = persist.AutoField()
    client = persist.ForeignKeyField(Client, backref='jobs')
    state = persist.CharField(max_length=32, choices=constants.JOB_STATES, index=True)

    added_moment = persist.DateTimeField()
    started_moment = persist.DateTimeField(null=True)
    ended_moment = persist.DateTimeField(null=True)

    timeout = persist.IntegerField(default=constants.DEFAULT_JOB_TIMEOUT)
    error = persist.CharField(max_length=256, default='')
    continue_on_failure = persist.BooleanField(default=False)

    flash_images_json = persist.TextField()
    assets_json = persist.TextField()
    test_cases_json = persist.TextField()
    results_json = persist.TextField(null=True)

    def __str__(self):
        return 'job{}'.format(self.id)

    @property
    def logger(self):
        return logging.getLogger('testmyesp.jobs.{}'.format(self))
