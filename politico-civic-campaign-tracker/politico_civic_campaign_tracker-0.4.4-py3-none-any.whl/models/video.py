from django.db import models
from election.models import Candidate


class Video(models.Model):
    """
    A video associated with a candidate
    """

    candidate = models.ForeignKey(
        Candidate, related_name="videos", on_delete=models.CASCADE
    )
    video_id = models.CharField(max_length=15)
    publish_date = models.DateTimeField()
    title = models.CharField(max_length=280, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
