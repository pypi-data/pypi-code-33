import re
import six
import datetime
import pytz
import dateutil.parser

def time_range_cutter_at_time(local,time_range,time_cut=(0,0,0)):
    """ Given a range, return a list of DateTimes that match the time_cut
        between start and end.

        :param local: if False [default] use UTC datetime. If True use localtz
        :param time_range: the TimeRange object
        :param time_cut: HH:MM:SS of when to cut. eg: (0,0,0) for midnight
    """

    ( start, end ) = time_range.get(local)
    index = start.replace(
                        hour=time_cut[0],
                        minute=time_cut[1],
                        second=time_cut[2]
                    )
    cuts = []
    index += datetime.timedelta(days=1)
    while index < end:
        cuts.append(index)

        index += datetime.timedelta(days=1)
        if local:
            index = time_range.normalize(index)
    return cuts

class TimeRange(object):
    start_time = None
    end_time = None

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def normalize(self,dt):
        return self.start_time.local_tz.normalize(dt)


    def get(self,local=False):
        return (
            self.start_time.get(local),
            self.end_time.get(local),
        )

    def delta(self,local=False):
        """ Returns the number of days of difference
        """
        (s,e) = self.get(local)
        return e-s

    def hours(self,local=False):
        """ Returns the number of hours of difference
        """
        delta = self.delta(local)
        return delta.total_seconds()/3600


    def days(self,local=False):
        """ Returns the number of days of difference
        """
        delta = self.delta(local)
        return delta.days

    def __contains__(self,timestamp):
        """ Returns true if the timestamp is found within this object's range

            :param timestamp: DateTime object of the time to test
        """
        if isinstance(timestamp,DateTime):
            return (
                    self.start_time >= timestamp
                and self.end_time <= timestamp
            )
        # TODO: also compare against another TimeRange in the future?
        else:
            return False

    def chunks(self,local,cutter_callback=None,*cutter_callback_args,**cutter_callback_kwargs):
        """ Takes a time range and returns sub timeranges based upon
            the cuts that cutter callback provides

            :param local: if False [default] use UTC datetime. If True use localtz
            :param cutter_callback: This should be a callback function that
                    takes the current TimeRange and returns a list of
                    DateTimes that denote where the next chunk should
                    start. By default the cutter used will cut at 00:00:00
                    each day.
        """

        # First we get all the slices we want to take out of this time range.
        if not cutter_callback:
            cutter_callback = time_range_cutter_at_time
        time_cuts = cutter_callback(local,self,*cutter_callback_args,**cutter_callback_kwargs)

        # Now we need to make the time range objects for the cuts
        time_chunks = []
        time_index = self.start_time
        time_cuts = sorted(time_cuts)
        for time_cut in time_cuts:

            # FIXME: Better error message is probably going to be helpful
            if self.end_time < time_cut or self.start_time > time_cut:
                raise Exception('Cut time provided that is outside of time range')

            # Create the new tail end entry for times, combine it with the
            # index to craft a timerange and add it to the chunk list
            cut_end_time = time_cut

            # If the chunk is not the final chunk, we want to pull
            # the time back by a small smidgen
            if cut_end_time != self.end_time:
                cut_end_time -= datetime.timedelta(microseconds=1)

            time_ending = DateTime(
                            data=cut_end_time,
                            data_tz=time_index.local_tz,
                            local_tz=time_index.local_tz
                            )


            chunk_range = TimeRange(time_index,time_ending)
            time_chunks.append(chunk_range)

            # Setup the index for the next cut (the current cut
            # becomes the start of the next cut)
            time_index = DateTime(
                            data=time_cut,
                            data_tz=time_index.local_tz,
                            local_tz=time_index.local_tz
                        )

        # Add the last segment if required
        if time_index != self.end_time:
            time_chunks.append(
                TimeRange(time_index,self.end_time)
            )

        return time_chunks

    def str(self,local):
        """ Return the string representation of the time range

            :param local: if False [default] use UTC datetime. If True use localtz
        """
        s = self.start_time.str(local) \
            + u" to " \
            + self.end_time.str(local)
        return s

    def __getattr__(self,k):
        m = re.search('^(utc|local)_(.*)$',k)
        if m:
            local = m.group(1) == 'local'
            n = m.group(2)
            return lambda *a,**kw: getattr(self,n)(local,*a,**kw)

        return object.__getattr__(self,k)

class Date(object):

    local_tz = None
    data = None

    def __init__(self,data,local_tz=None,tz_name=None):
        if isinstance(data,Date):
            self.local_tz = data.local_tz
            self.data = data
        else:
            if local_tz:
                self.local_tz = local_tz
            elif tz_name:
                self.local_tz = pytz.timezone(tz_name)
            else:
                self.local_tz = pytz.utc

            if isinstance(data,six.string_types):
                self.data = dateutil.parser.parse(data).date()
            else:
                self.data = data

    def localize(self,local=False,time_data=None):
        if not time_data: return time_data
        if local:
            return self.local_tz.localize(time_data)
        return pytz.utc.localize(time_data)

    def start_time(self,local=False):
        time_data = datetime.datetime(
                            self.data.year,
                            self.data.month,
                            self.data.day,
                            0,
                            0,
                            0,
                            0,
                        )
        time_data = self.localize(local,time_data)
        return DateTime(time_data,self.local_tz,self.local_tz)

    def end_time(self,local=False):
        time_data = datetime.datetime(
                            self.data.year,
                            self.data.month,
                            self.data.day,
                            23,
                            59,
                            59,
                            999999,
                        )
        time_data = self.localize(local,time_data)
        return DateTime(time_data,self.local_tz,self.local_tz)

    def str(self,local=False):
        return self.data.isoformat()
    def __str__(self):
        return self.data.isoformat()

    def __getattr__(self,k):
        m = re.search('^(utc|local)_(.*)$',k)
        if m:
            local = m.group(1) == 'local'
            n = m.group(2)
            return lambda *a,**kw: getattr(self,n)(local,*a,**kw)

        return object.__getattr__(self,k)


class DateTime(object):

    # The timestamp we care about in UTC
    utc_data = None

    # The timezone we use for local transformations
    local_tz = None

    # The timestamp in local_tz
    local_data = None

    def __init__(self,data,data_tz,local_tz,tz_name=None):
        """ Accepts either a string or an existing datetime and loads it up
        """
        self.local_tz = local_tz

        # Is this a string?
        if isinstance(data,six.string_types):
            timestamp = dateutil.parser.parse(data)

            # If we notice that there is an offset and that it's
            # UTC, let's ensure that it's using pytz.utc. There's this
            # weird error that I never got to the bottom of that somtimes
            # the timestamp.tzinfo turns into tzlocal. SO WEIRD! While
            # this isn't a true fix, as I don't know why it would randomly
            # switch to tzlocal despite a +00:00, this will let the code
            # do its job and "corrects" behaviour.
            if re.search(r'\+00:00',data):
                timestamp = timestamp.replace(tzinfo = pytz.utc)

            # Handle things differently based upon whether or not we have a timezone
            if timestamp.tzinfo:
                self.utc_data = timestamp.astimezone(pytz.utc)
                self.local_data = self.utc_data.astimezone(local_tz)
            else:
                timestamp = data_tz.localize(timestamp)
                self.utc_data = timestamp.astimezone(pytz.utc)
                self.local_data = timestamp.astimezone(local_tz)

        # Is it an existing DateTime?
        elif isinstance(data,DateTime):
            self.utc_data = data.utc_data
            self.local_tz = data.local_tz
            self.local_data = data.local_data

        # Is it a datetime?
        elif isinstance(data,datetime.datetime):
            # is it a naive datetime? if so we'll append a TZ to it
            if not data.tzinfo:
                timestamp = data_tz.localize(data)
                self.utc_data = timestamp.astimezone(pytz.utc)
                self.local_data = timestamp.astimezone(local_tz)

            else:
                self.utc_data = data.astimezone(pytz.utc)
                self.local_data = self.utc_data.astimezone(local_tz)

    def daily_hours(self,local=False):
        """ This returns a number from 0 to 24 that describes the number
            of hours passed in a day. This is very useful for hr.attendances
        """
        data = self.get(local)
        daily_hours = (data.hour +
                       data.minute / 60.0 +
                       data.second / 3600.0)
        return round(daily_hours,2)

    def get(self,local=False):
        """ Return the datetime object based upon whether we want the local
            or utc one.

            :param local: if False [default] return UTC datetime. If True return localtz
        """
        if local:
            return self.local_data
        return self.utc_data

    def date(self,local=False):
        """ Return the date object associated
            :param local: if False [default] return UTC date. If True return localtz date
        """
        return Date(self.get(local).date(),self.local_tz)

    def str(self,local=False,ifempty=None):
        """ Returns the string representation of the datetime
        """
        ts = self.get(local)
        if not ts: return ifempty
        return ts.strftime('%Y-%m-%d %H:%M:%S')

    def __getattr__(self,k):
        m = re.search('^(utc|local)_(.*)$',k)
        if m:
            local = m.group(1) == 'local'
            n = m.group(2)
            return lambda *a,**kw: getattr(self,n)(local,*a,**kw)

        return object.__getattr__(self,k)

    def __eq__(self,v):
        """ Handle == comparison
        """
        if isinstance(v,DateTime):
            return self.utc_data == v.utc_data
        elif isinstance(v,datetime.datetime):
            return self.utc_data == v
        return NotImplemented

    def __ne__(self,v):
        """ Handle != comparison
        """
        if isinstance(v,DateTime):
            return self.utc_data != v.utc_data
        elif isinstance(v,datetime.datetime):
            return self.utc_data != v
        return NotImplemented

    def __gt__(self,v):
        """ Handle > comparison
        """
        if isinstance(v,DateTime):
            return self.utc_data > v.utc_data
        elif isinstance(v,datetime.datetime):
            return self.utc_data > v
        return NotImplemented

    def __ge__(self,v):
        """ Handle >= comparison
        """
        if isinstance(v,DateTime):
            return self.utc_data >= v.utc_data
        elif isinstance(v,datetime.datetime):
            return self.utc_data >= v
        return NotImplemented

    def __lt__(self,v):
        """ Handle < comparison
        """
        if isinstance(v,DateTime):
            return self.utc_data < v.utc_data
        elif isinstance(v,datetime.datetime):
            return self.utc_data < v
        return NotImplemented

    def __le__(self,v):
        """ Handle <= comparison
        """
        if isinstance(v,DateTime):
            return self.utc_data <= v.utc_data
        elif isinstance(v,datetime.datetime):
            return self.utc_data <= v
        return NotImplemented

class DateTimeLocal(DateTime):
    def __init__(self,data,tz_name=None,tz=None):
        """ Accepts either a string or an existing datetime and loads it up
        """
        if tz:
            local_tz = pytz.timezone(tz)
        elif tz_name:
            local_tz = pytz.timezone(tz_name)
        else:
            local_tz = pytz.utc
        super(DateTimeLocal,self).__init__(
                data,
                data_tz=local_tz,
                local_tz=local_tz,
                tz_name=tz_name)

class DateTimeUTC(DateTime):
    def __init__(self,data,tz_name=None,tz=None):
        """ Accepts either a string or an existing datetime and loads it up
        """
        if tz:
            local_tz = pytz.timezone(tz)
        elif tz_name:
            local_tz = pytz.timezone(tz_name)
        else:
            local_tz = pytz.utc
        super(DateTimeUTC,self).__init__(
                data,
                data_tz=pytz.utc,
                local_tz=local_tz,
                tz_name=tz_name)

# Just for testing purposes
if __name__ == '__main__':
    tz_name = 'America/Vancouver'
    a = DateTimeLocal('2017-01-01 09:03:01',tz_name=tz_name)
    b = DateTimeLocal('2017-01-11 21:51:32',tz_name=tz_name)

    six._print(a.local_str())
    six._print(">",a.utc_str())

    six._print(b.local_str())
    six._print(">",b.utc_str())

    r = TimeRange(a,b)
    six._print("Local day difference",r.local_days())
    six._print("UTC day difference",r.utc_days())

    for c in r.local_chunks():
        six._print(c.local_str())


    d = Date('2018-02-16',tz_name=tz_name)
    six._print(d)
    six._print(d.local_start_time().local_str())
    six._print(d.utc_end_time().local_str())

    six._print("Trying UTC changes")
    d = DateTimeUTC(u'2018-03-01T22:05:13+00:00',tz_name)
    six._print(d.utc_str())
    six._print(d.local_str())


    d = DateTimeUTC(u'2018-03-01T22:05:13+00:00',tz_name)
    six._print(d.utc_str())
    six._print(d.local_str())

