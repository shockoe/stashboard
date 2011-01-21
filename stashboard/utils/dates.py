# Various date helpers

import pytz
import logging

from datetime import timedelta
from stashboard import config

def add_offset(d):
    """ Take a naive datetime and add the offset timezone. Does not
    shift the time or date, and the date is still naive
    """
    utc = pytz.utc
    stash_tz = get_timezone()
    dn = stash_tz.localize(d)
    return dn.astimezone(utc).replace(tzinfo=None)

def get_timezone():
    """ Return the timezone set in CONFIG. 

    If no time zone set, or given an improper timezone, retuen UTC"""
    try:
        return pytz.timezone(config.TIMEZONE)
    except:
        return pytz.utc

def localize(d):
    """ Take a naive datetime, localize via the set timezone
    """
    utc = pytz.utc
    stash_tz = get_timezone()
    d = d.replace(tzinfo=utc)
    return stash_tz.normalize(d)

