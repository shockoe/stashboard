# Copyright (c) 2010 Twilio Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
import pytz
import urlparse

from datetime import timedelta
from datetime import datetime
from datetime import date
from time import mktime
from wsgiref.handlers import format_date_time

from google.appengine.ext import db

from stashboard import config
from stashboard.utils import dates

class Level(object):
    """A fake db.Model, just in case we want to actually store things."""

    levels = {
        "NORMAL": 10,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }
    
    normal  = "NORMAL"
    warning = "WARNING"
    critial = "CRITICAL"
    error   = "ERROR"
    
    @staticmethod
    def all():
        """Fetches all valid status levels.

        Returns:
          levels: A list of Level instances
        """
        llist = [(k, Level.levels[k]) for k in Level.levels.keys()]
        return map(lambda x: x[0], sorted(llist, key=lambda x: x[1]))
        
    @staticmethod
    def get_severity(level):
        """Get the severity of a given level.

        Returns False if the given level doesn't exist.
        
        Returns:
          int: status severity
        """
        try:
            return Level.levels[level]
        except:
            return False
            
    @staticmethod
    def get_level(severity):
        """For a given severity, return the correct level.

        Returns False if no level for given severity.

        Returns:
          str: status Level
        """
        for k in Level.levels.keys():
            if Level.levels[k] == severity:
                return k
        return False
     

class Service(db.Model):
    """A service for Stashaboard to track."""

    @staticmethod
    def get_by_slug(service_slug):
        """Fetches a service by the given service_slug.

        Args:
          service_slug: Service name

        Returns:
          A Service instance or None if no service can be found.
        """
        return Service.all().filter('slug = ', service_slug).get()
        
    
    slug = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    
    def sid(self):
        """Get the service string identifier.
        
        Returns:
          The string identifier for this Service instance.
        """
        return unicode(self.key())

    def current_event(self):
        """ Fecth the current event.
        
        Returns:
          The current Event instance for this Service.
        """
        event = self.events.order('-start').get()
        return event

    def calendar(self, start, n):
        """ Return the calendar report for the given range (inclusive).

        Args:
          start: A datetime object starting the range
          n: The number of days to return

        Returns:
          A list of dictionaries. One dictionary for each of the last five days.
        """
        lowest = Status.default()
        severity = lowest.severity

        end = start - timedelta(days=n)
        events = self.events.filter('start >=', end) \
            .filter('start <=', start).fetch(100)
        
        stats = []
        
        for i in range(n):
            start -= timedelta(days=1)
            stats.append({
                "image": lowest.image,
                "day": start,
                "information": False,
                "events": [],
            })
        
        for event in events:
            for i in range(n):
                day = stats[i]["day"]
                if event.start >= day and event.start < (day + timedelta(days=1)):
                    stats[i]["events"].append(event)
                    if event.status.severity > severity:
                        stats[i]["image"] = "information"
                        stats[i]["information"] = True

        return stats


    def last_six_days(self):
        """ Fetch the last five days of events.

        A day is represented by a dictionary with the image of the highest
        severity event and a Date object for that day. If the severity is
        greater than a normal event, an "information" flag is set to True.

        Returns:
          A list of dictionaries. One dictionary for each of the last five days.
        """
        utc = pytz.utc
        stash_tz = dates.get_timezone()
        d = datetime.now().replace(tzinfo=utc)
        dn = stash_tz.normalize(d).replace(hour=0, minute=0, second=0, microsecond=0)
        dn += timedelta(days=1)
        dn = dn.astimezone(utc).replace(tzinfo=None)
        logging.info(dn)
        calendar = self.calendar(dn, 6)
        return calendar

    def events_for_day(self, day):
        """Fetch the Events for a given day.
        
        Args: 
          day: A date object:
        
        Returns:
          A list of Events, or None if no events happend on this day
        """
        next_day = day + timedelta(days=1)
        
        return self.events.filter('start >=', day) \
            .filter('start <', next_day).fetch(40)
            
    def resource_url(self):
        """Returns the service's resource url.

        TODO: These urls should not be hardcoded in the model class

        Returns:
          A relative URL to this resource
        """
        return "/services/" + self.slug
        
    def rest(self, base_url):
        """Return a dict representing this model

        This object represents the Service in the REST API

        Returns:
          A dictionary
        """
        m = {}
        m["name"] = unicode(self.name)
        m["id"] = unicode(self.slug)
        m["description"] = unicode(self.description)
        m["url"] = base_url + self.resource_url()
        
        event = self.current_event()
        if event:
            m["current-event"] = event.rest(base_url)
        else:
            m["current-event"] = None

        return m

class Status(db.Model):
    """A possible system status

        Properties:
        name        -- string: The friendly name of this status
        slug        -- stirng: The identifier for the status
        description -- string: The state this status represents
        image       -- string: Image in /images/status
        severity    -- int: The serverity of this status

    """
    @staticmethod
    def get_by_slug(status_slug):
        """Fetch a Status for a given name

        Args:
          status_slug: A name of a possible status

        Returns:
          A Status instance or None if no Status has the name service_slug
        """
        return Status.all().filter('slug = ', status_slug).get()
        
    @staticmethod
    def default():
        """Fetch the first status with a NORMAL level.
        
        Returns:
          A Status instance, or None if no Status has a NORMAL level
        """
        normal = Level.get_severity(Level.normal)
        return Status.all().filter('severity == ', normal).get()

    @staticmethod
    def install_defaults():
        """Install the default statuses. 

        After creating and persisting the three default statuses, we create
        a Setting object to signal the that the installation was successful.
        """
        normal = Level.get_severity(Level.normal)
        warning = Level.get_severity(Level.warning)
        error = Level.get_severity(Level.error)

        d = Status(name="Down", slug="down", image="cross-circle", severity=error, \
                       description="The service is currently down")
        u = Status(name="Up", slug="up", image="tick-circle", severity=normal, \
                       description="The service is up")
        w = Status(name="Warning", slug="warning", image="exclamation", severity=warning, \
                       description="The service is experiencing intermittent problems")

        d.put()
        u.put()
        w.put()

        s = Setting(name="installed_defaults")
        s.put()
        
        
    name = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    image = db.StringProperty(required=True)
    severity = db.IntegerProperty(required=True)
    
    def image_url(self):
        """Returns the status's image url.

        TODO: These urls should not be hardcoded in the model class

        Returns:
          A relative URL to the image for this resource
        """
        return "/images/status/" + unicode(self.image) + ".png"
        
    def resource_url(self):
        """Returns the status's url.

        TODO: These urls should not be hardcoded in the model class

        Returns:
          A relative URL for this resource
        """
        return "/statuses/" + unicode(self.slug)
        
    def rest(self, base_url):
        """Return a dict representing this model.

        This object represents the Status in the REST API.
        TODO: The image url creation should not be handled in the
        model

        Returns:
          A dictionary
        """
        m = {}
        m["name"] = unicode(self.name)
        m["id"] = unicode(self.slug)
        m["description"] = unicode(self.description)
        m["level"] = Level.get_level(int(self.severity))
        m["url"] = base_url + self.resource_url()
        o = urlparse.urlparse(base_url)
        m["image"] = o.scheme + "://" +  o.netloc + self.image_url()
        
        return m
    

class Event(db.Model):
    """A service event.

        Properties:
        start         -- DateTime: The time this event occurred
        informational -- bool: True if this event has information attached
        status        -- Status: The Status associated with this event
        message       -- string: The message for this event
        service       -- Service: The Service this event belongs to
    """
    start = db.DateTimeProperty(required=True, auto_now_add=True)
    informational = db.BooleanProperty(default=False)
    status = db.ReferenceProperty(Status, required=True)
    message = db.TextProperty(required=True)
    service = db.ReferenceProperty(Service, required=True, 
        collection_name="events")
        
    def sid(self):
        """Get the event string identifier.
        
        Returns:
          The string identifier for this Event instance.
        """
        return unicode(self.key())

    def local_start(self):
        """Get the start time, local to the timezone in config

        Returns:
          A datettime object
        """
        return dates.localize(self.start)

    def resource_url(self):
        """Returns the event's resource url.

        TODO: These urls should not be hardcoded in the model class

        Returns:
          A relative URL to this resource
        """
        return self.service.resource_url() + "/events/" + self.sid()
    
    def rest(self, base_url):
        """Return a dict representing this model.

        This object represents the Event in the REST API.

        Returns:
          A dictionary
        """
        m = {}
        m["sid"] = self.sid()

        stamp = mktime(self.start.timetuple())
        m["timestamp"] = format_date_time(stamp)
        m["status"] = self.status.rest(base_url)
        m["message"] = unicode(self.message)
        m["url"] = base_url + self.resource_url()

        if self.informational:
            m["informational"] = self.informational
        else:
            m["informational"] = False
        
        return m
        
class Profile(db.Model):
    """A Profile stores API credentials for a user"""
    owner = db.UserProperty(required=True)
    token = db.StringProperty(required=True)
    secret = db.StringProperty(required=True)

class AuthRequest(db.Model):
    """An AuthRequest saves the request token for OAuth validation"""
    owner = db.UserProperty(required=True)
    request_secret = db.StringProperty()

class Setting(db.Model):
    """Settings are proof that certain actions take place. 

    This object is used when installed default statuses. See
    Status.install_statuses() for more information.
    """
    name = db.StringProperty(required=True)

