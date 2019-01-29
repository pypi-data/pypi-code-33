from django.db import models
from election.models import Candidate


class Quote(models.Model):
    """
    Quotes spoken.
    """

    candidate = models.ForeignKey(
        Candidate, related_name="quotes", on_delete=models.CASCADE
    )
    text = models.TextField()
    date = models.DateField()
    place = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="If known, name the location where speaker spake.",
    )
    link = models.URLField(
        blank=True,
        null=True,
        help_text="If available, add a link to the quote on social"
        " media or as published online.",
    )

    @property
    def truncated(self):
        return " ".join(self.text.split()[:10])

    @property
    def speaker(self):
        return self.biography.person.full_name

    def __str__(self):
        return "{} {}".format(
            self.date.strftime("%Y-%m-%d"), self.candidate.person.full_name
        )
