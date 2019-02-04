####
# bomail.util.datestuff
#
# Everything dealing with the mess that is date and time.
####

import datetime
import dateutil.parser
import pytz
from dateutil import tz
from dateutil.relativedelta import relativedelta
import traceback
import email, email.utils

datestr_str = """
'date strings' are used in search and scheduling, e.g.
    bomail search -a datestr   # search after given date
    bomail chstate -s datestr  # schedule for given date

datestr can be in:
 (1) Absolute format: yyyy-mm-ddTHH:MM
     or any prefix of this.

 (2) Relative format: p[num][unit]
     meaning plus num of units from now.
     Unit can be y (year), w (week), H (hour), M (minute).
     month is not allowed, to avoid confusing with minute.
     If num has a decimal point, adds the exact amount.
     Else, rounds down to the nearest unit.

 (3) Relative format:  m[num][unit]
     meaning minus num of units before now.
     Same details as (2) apply.

Some examples for absolute date:
  2050              # Jan 1st, 2050 at 00:00
  2050-03-07        # Mar 7th, 2050 at 00:00
  2050-03-07T11     # Mar 7th, 2050 at 11:00

Some examples for relative date:
  p1d               # tomorrow at 00:00, no matter what time it is today
  p1.d              # tomorrow at the same time of day that it is right now
  p1.5d             # 36 hours from now
  m3w               # 3 weeks before now, rounded down to Monday at 00:00
  m3.5w             # exactly 3.5 weeks before now (to the minute)
"""



# parse the email's date string and return a datetime object
def parse_email_date(s):
  if len(s) == 0:
    return datetime.datetime(9999,12,30)
  if "A.D." in s:  # remove this, is messes up the parser
    i = s.index("A.D.")
    s = s[:i] + (s[i+4:] if i+4 < len(s) else "")
  try:
    result = email.utils.parsedate_to_datetime(s)
    if result:  # if timezeone-unaware, should be UTC time
      if result.tzinfo is None:
        result = result.replace(tzinfo=pytz.utc)
      return result
    return datetime.datetime(9999,12,28)
  except:
    return datetime.datetime(9999,12,29)

# return datetime object for UTC time right now, timezone-aware
def get_utc_nowobj():
  return datetime.datetime.now(datetime.timezone.utc)

def parse_to_utc_obj(datestr):
  dateobj = dateutil.parser.parse(datestr)
  if dateobj.tzinfo is None:
    dateobj = dateobj.replace(tzinfo=pytz.utc)
  return dateobj.astimezone(pytz.utc)

def parse_to_utc_datestr(datestr):
  return parse_to_utc_obj(datestr).isoformat()

# convert object to local-time object
def parse_to_local_obj(datestr):
  dateobj = dateutil.parser.parse(datestr)
  if dateobj.tzinfo is None:
    dateobj = dateobj.replace(tzinfo=pytz.utc)
  return dateobj.astimezone(tz.tzlocal())

# convert object to local ISO string
def get_local_str(dateobj):
  loc = dateobj.astimezone(tz.tzlocal())
  return loc.isoformat()

def get_local_nowstr():
  return datetime.datetime.now(tz.tzlocal()).isoformat()

# filename is ...email/yyyy/mm-dd/x.email
# or something.draft
def get_date_from_filename(filename):
  # filedir = os.path.dirname(filename)  # too slow
  slashind = filename.rfind("/")  # assume x does not contain a slash!!
  return filename[slashind-10:slashind].replace("/","-")


def datestr_matches(datestr, after, before):
  return ((after is None or datestr[:len(after)] >= after)
           and (before is None or datestr[:len(before)] <= before))

def filename_matches_date(fname, after, before):
  return datestr_matches(get_date_from_filename(fname), after, before)


# ------------------------------------
# parsing schedstr strings


# given a 'schedstr' like yyyy-mm or m3.0d,
# turn it into an absolute date string yyyy-mm-ddT...
# in local time zone, throw an exception if unable
#def get_absstr_from_datestr(schedstr):
#  dateobj = get_datetime(schedstr)
#  if dateobj is None:
#    dateobj = datetime.datetime.now(tz.tzlocal())
#  try:
#    dateobj = dateobj.astimezone(tz.tzlocal())
#  except:
#    dateobj = pytz.utc.localize(dateobj)
#  return dateobj.isoformat()[:16]



def get_relativedelta_int(num, suffix):
  if suffix == "y":
    return relativedelta(years=int(num))
  elif suffix == "w":
    return relativedelta(weeks=int(num))
  elif suffix == "d":
    return relativedelta(days=int(num))
  elif suffix == "H":
    return relativedelta(hours=int(num))
  else:  # "M"
    return relativedelta(minutes=int(num))



def get_relativedelta_float(num, suffix):
  if num < 0:
    return -get_relativedelta_float(-num, suffix)
  
  inum = int(num)
  if suffix == "y":
    return relativedelta(years=inum) + get_relativedelta_float((num-inum)*365, "d")
  elif suffix == "w":
    return relativedelta(weeks=inum) + get_relativedelta_float((num-inum)*7, "d")
  elif suffix == "d":
    return relativedelta(days=inum) + get_relativedelta_float((num-inum)*24, "H")
  elif suffix == "H":
    return relativedelta(hours=inum) + get_relativedelta_float((num-inum)*60, "M")
  else:  # "M"
    return relativedelta(minutes=inum)

def get_relativedelta(num, suffix, is_float):
  if is_float:
    return get_relativedelta_float(num, suffix)
  else:
    return get_relativedelta_int(num, suffix)


# convert schedule string to datetime object in UTC
# or None if failure
def parse_schedstr_to_utcobj(schedstr):
  if schedstr[0] == "p":
    mult = 1.0  # forward in time
  elif schedstr[0] == "m":
    mult = -1.0  # backward in time
  else: # absolute date: parse it and return
    try:
      return parse_to_utc_obj(schedstr)
    except:
      return None

  # if we get to here, it's a relative
  nowobj = get_utc_nowobj()
  numstr = schedstr[1:-1]
  num = mult*float(numstr)  # forward or back in time
  suffix = schedstr[-1]
  diff = None
  is_float = "." in numstr
  result = nowobj + get_relativedelta(num, suffix, is_float)
  default_obj = datetime.datetime(1,1,1,tzinfo=pytz.utc)

  if not is_float:  # round the answer
    if suffix == "y":
      result = default_obj.replace(result.year)
    elif suffix == "w":
      dayoffset = relativedelta(days=result.weekday())
      result = default_obj.replace(year=result.year, month=result.month, day=result.day) - dayoffset
    elif suffix == "d":
      result = default_obj.replace(year=result.year, month=result.month, day=result.day)
    elif suffix == "H":
      result = default_obj.replace(year=result.year, month=result.month, day=result.day, hour=result.hour)
    elif suffix == "M":
      result = default_obj.replace(year=result.year, month=result.month, day=result.day, hour=result.hour, minute=result.minute)

  return result


def parse_schedstr_to_utcstr(schedstr):
  dateobj = parse_schedstr_to_utcobj(schedstr)
  return dateobj.isoformat()


# given date object, get date string to print in schedule file
def get_printed_schedulestr(dateobj):
  rounded_date = dateobj.replace(second=0, microsecond=0)
  return rounded_date.astimezone(pytz.utc).isoformat()




