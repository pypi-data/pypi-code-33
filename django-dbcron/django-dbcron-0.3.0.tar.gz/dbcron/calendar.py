from datetime import date, timedelta, datetime
from calendar import HTMLCalendar
from django.utils.translation import ugettext_lazy as _
from dbcron import models

DAYS = {
    0: _("Sunday"),
    1: _("Monday"),
    2: _("Tuesday"),
    3: _("Wednesday"),
    4: _("Thursday"),
    5: _("Friday"),
    6: _("Saturday"),
}


class JobCalendar(HTMLCalendar):
    table_class = ""
    ul_class = ""

    def __init__(self, jobs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jobs = jobs

    def get_table_class(self):
        return self.table_class

    def formatmonth(self, theyear, themonth, withyear=True):
        v = []
        a = v.append
        a('<table class="%s">' % (
            self.get_table_class()
        ))
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def itermonthweekdays(self, theyear, themonth, theweek):
        for day_ in self.itermonthdates(theyear, themonth):
            if day_.isocalendar()[1] != theweek:
                continue
            yield day_

    def get_firstdateofweek(self, theyear, theweek):
        year_date = date(theyear, 1, 1)
        week_date = year_date + timedelta(days=theweek*7)
        first_day = week_date - timedelta(days=week_date.isocalendar()[1])
        return first_day

    def _format_weekday(self, day):
        return str(DAYS[day])

    def _format_hour(self, hour):
        if hour == 0:
            return str(_("Midnight"))
        elif hour == 12:
            return str(_("Noon"))
        return '%d' % hour

    def _format_jobs(self, v, first_day, dates):
        a = v.append
        for hour in range(0, 24):
            day = first_day
            a('<tr>')
            a('<th>')
            a(self._format_hour(hour))
            a('</th>')
            for i in range(7):
                a('<td>')
                a('<ul class="%s">' % self.ul_class)
                for job, jobtime in dates[day][hour]:
                    a('<li>')
                    if hasattr(job, 'get_absolute_url'):
                        a('%s - <a href="%s">%s</a>' % (jobtime.strftime("%M"),
                                                        job.get_absolute_url(),
                                                        job.name))
                    else:
                        a('%s - %s' % (jobtime.strftime("%H:%M"), job.name))
                    a('</li>')
                a('</ul>')
                a('</td>')
                day += timedelta(days=1)
            a('</tr>')
            a('\n')

    def formatweekofmonth(self, theyear, theweek, withyear=True):
        v = []
        a = v.append
        a('<table class="%s">' % (
            self.get_table_class()
        ))
        a('\n')
        a('<tr>')
        a('<th>%s</th>' % _("UTC"))
        for i in range(7):
            a('<th>%s</th>' % self._format_weekday(i))
        a('</tr>')
        day = self.get_firstdateofweek(theyear, theweek)
        dates = self.jobs.get_next_planned_by_hour(
            from_=datetime(theyear, day.month, day.day-1, 23, 59),
            until=day+timedelta(days=7))
        a('<tr>')
        self._format_jobs(v, day, dates)
        a('<tr>')
        a('</table>')
        a('\n')
        return ''.join(v)
