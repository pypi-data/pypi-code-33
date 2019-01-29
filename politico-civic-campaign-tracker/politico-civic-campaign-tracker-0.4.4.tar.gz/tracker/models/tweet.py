from django.db import models
from election.models import Candidate


class Tweet(models.Model):
    """
    A tweet associated with a candidate
    """

    candidate = models.ForeignKey(
        Candidate,
        related_name="tweets",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    url = models.URLField()
    publish_date = models.DateTimeField()
    tweet_text = models.CharField(max_length=280)
    tweet_handle = models.CharField(max_length=30)

    def __str__(self):
        return "{}: {}".format(self.tweet_handle, self.tweet_text)
