from django.db import models
from election.models import Candidate


class Story(models.Model):
    """
    A story associated with a candidate
    """

    candidate = models.ForeignKey(
        Candidate, related_name="stories", on_delete=models.CASCADE
    )
    url = models.URLField()
    headline = models.CharField(max_length=140)
    description = models.TextField(null=True, blank=True)
    image_url = models.URLField()
    publish_date = models.DateTimeField()
    byline = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.headline
