import pytz
from datetime import datetime
from datetime import timedelta

utc = pytz.utc
pacific = pytz.timezone("US/Pacific")

d = datetime.now().replace(tzinfo=utc)
l = pacific.normalize(d)

if d == l:
    print "hey"
    print d
    print l

p = d + timedelta(days=3)
td = d - p
print abs(td.days)
