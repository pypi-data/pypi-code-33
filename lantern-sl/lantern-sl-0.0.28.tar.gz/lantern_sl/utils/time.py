import datetime

def current_ts(tz=datetime.timezone.utc):
    """ returns the current timestamp for the specified timezone """
    return int(datetime.datetime.now(tz).timestamp()*1000)

# Dummy Line