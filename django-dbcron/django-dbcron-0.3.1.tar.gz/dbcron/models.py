import importlib
import json
from datetime import timedelta
from crontab import CronTab
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from dbcron import validators
from dbcron import querysets


class Job(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("name"))
    tag = models.CharField(max_length=150, verbose_name=_("tag"), blank=True, null=True)
    description = models.TextField(max_length=2000, verbose_name=_("description"), blank=True)
    func = models.CharField(max_length=250, verbose_name=_("function"))

    args = models.TextField(max_length=2000, default='[]', verbose_name=_("arguments"))
    opts = models.TextField(max_length=2000, default='{}', verbose_name=_("options"))

    is_active = models.BooleanField(default=False, verbose_name=_("is active"))

    sec = models.CharField(
        max_length=50, default='0', verbose_name=_("second(s)"),
        validators=[validators.SecondsValidator()]
    )
    min = models.CharField(
        max_length=50, verbose_name=_("minute(s)"),
        validators=[validators.MinutesValidator()]
    )
    hou = models.CharField(
        max_length=50, verbose_name=_("hour(s)"),
        validators=[validators.HoursValidator()]
    )
    dom = models.CharField(
        max_length=50, verbose_name=_("day(s) of month"),
        validators=[validators.DaysOfMonthValidator()]
    )
    mon = models.CharField(
        max_length=50, verbose_name=_("month"),
        validators=[validators.MonthValidator()]
    )
    dow = models.CharField(
        max_length=50, verbose_name=_("day(s) of week"),
        validators=[validators.DaysOfWeekValidator()]
    )
    yea = models.CharField(
        max_length=50, default='*', verbose_name=_("year(s)"),
        validators=[validators.YearsValidator()]
    )

    objects = querysets.JobQuerySet.as_manager()

    class Meta:
        verbose_name = _("job")
        verbose_name_plural = _("jobs")

    @property
    def raw_entry(self):
        return ' '.join([self.sec, self.min, self.hou, self.dom, self.mon,
                         self.dow, self.yea])

    def __str__(self):
        return "%s (%s)" % (self.name, self.raw_entry)

    @property
    def entry(self):
        return CronTab(self.raw_entry.strip())

    def _get_func(self):
        module_path = '.'.join(self.func.split('.')[:-1])
        func_name = self.func.split('.')[-1]
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        return func

    def run(self):
        func = self._get_func()
        args = json.loads(self.args)
        opts = json.loads(self.opts)
        result = func(*args, **opts)
        return result

    @property
    def next_time(self):
        next_ = self.entry.next()
        if next_ is not None:
            return int(self.entry.next())

    def get_next_planned(self, until, from_):
        from_ = from_ or now()
        while until > from_.date():
            delta = self.entry.next(from_)
            from_ += timedelta(seconds=delta)
            if delta < 1:
                continue
            yield from_
