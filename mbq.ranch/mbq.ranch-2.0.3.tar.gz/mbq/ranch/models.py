from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class LoggedTask(models.Model):
    id = models.CharField(max_length=255, primary_key=True, unique=True)
    queue = models.CharField(max_length=128, null=True)
    task_name = models.CharField(max_length=2056)
    status = models.CharField(max_length=50)
    args = models.TextField(default="[]")
    kwargs = models.TextField(default="{}")
    stacktrace = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rollbar_occurrence = models.UUIDField(null=True)

    def __str__(self):
        return "{} - args: {}, kwargs {}".format(self.task_name, self.args, self.kwargs)
