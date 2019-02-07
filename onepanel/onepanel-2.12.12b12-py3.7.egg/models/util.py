import iso8601

def parse_date(date_string):
    if date_string is None:
        return None

    return iso8601.parse_date(date_string)
    
def format_timedelta(value):
    """Takes a timedelta value and converts it to dd:hh:mm:ss or hh:mm:ss if days are 0"""

    if value is None:
        return '00:00:00'

    days, remainder = divmod(value.total_seconds(), 86400) #86400 seconds in a day
    hours, remainder = divmod(remainder, 3600) #3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60) #60 seconds in a minute

    if days > 0:
        return '{:02}:{:02}:{:02}:{:02}'.format(int(days), int(hours), int(minutes), int(seconds))

    #three spaces for days and colon
    return '   {:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))