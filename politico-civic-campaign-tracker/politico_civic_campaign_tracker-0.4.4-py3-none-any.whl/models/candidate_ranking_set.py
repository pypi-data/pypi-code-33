from django.db import models


class CandidateRankingSet(models.Model):
    date = models.DateField()

    def __str__(self):
        return "{} ranking set".format(self.date.strftime("%m-%d-%y"))
