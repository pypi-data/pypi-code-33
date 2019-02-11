from collections import defaultdict
from django.db import models


class JobQuerySet(models.QuerySet):
    def get_next_planned_by_day(self, until, from_=None):
        dates = defaultdict(list)
        for job in self.all():
            for next_date in job.get_next_planned(until, from_):
                dates[next_date.date()].append((job, next_date))
        for date in dates:
            dates[date] = sorted(dates[date], key=lambda x: x[1])
        return dates

    def get_next_planned_by_hour(self, until, from_=None):
        dates = defaultdict(lambda: defaultdict(list))
        for job in self.all():
            for next_date in job.get_next_planned(until, from_):
                dates[next_date.date()][next_date.hour].append((job, next_date))
        for date in dates:
            for hour in dates[date]:
                dates[date][hour] = sorted(dates[date][hour], key=lambda x: x[1])
        return dates
