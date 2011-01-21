import unittest

from stashboard import models
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub

APP_ID = "stashboard"

class StashboardTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        self.clear_datastore()
        super(StashboardTest, self).setUp(*args, **kwargs)

    def clear_datastore(self):
        from google.appengine.api import apiproxy_stub_map, datastore_file_stub
        # Use a fresh stub datastore.
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        stub = datastore_file_stub.DatastoreFileStub(APP_ID, '/dev/null',
                                                     '/dev/null')
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)

class TestServices(StashboardTest):
    """Unit tests for the Service model"""

    def test_creation(self):
        s = models.Service(slug="service-foo", name="Service Foo", 
                           description="A wonderful service")
        s.put()
        fetched_s = models.Service.get_by_slug("service-foo")
        self.assertEqual(fetched_s.name, "Service Foo")
        self.assertEqual(fetched_s.slug, "service-foo")
        self.assertEqual(fetched_s.description, "A wonderful service")
        self.assertEqual(fetched_s.current_event(), None)

    def test_invalid_service_slug(self):
        """ An invalid service slug shoud cause Service.get_by_slug to
        return None.
        """
        fetched = models.Service.get_by_slug("doesntexists")
        self.assertEqual(fetched, None) 

class TestLevels(StashboardTest):

    def test_all(self):
        expected = ['NORMAL', 'WARNING', 'ERROR', 'CRITICAL']
        levels = models.Level.all()
        self.assertEqual(levels, expected)

    def test_get_severity(self):
        normal = models.Level.get_severity("NORMAL")
        warning = models.Level.get_severity("WARNING")
        error = models.Level.get_severity("ERROR")
        critical = models.Level.get_severity("CRITICAL")
        self.assertEqual(normal, 10)
        self.assertEqual(warning, 30)
        self.assertEqual(error, 40)
        self.assertEqual(critical, 50)

    def test_get_level(self):
        normal = models.Level.get_level(10)
        warning = models.Level.get_level(30)
        error = models.Level.get_level(40)
        critical = models.Level.get_level(50)
        self.assertEqual(normal, "NORMAL")
        self.assertEqual(warning, "WARNING")
        self.assertEqual(error, "ERROR")
        self.assertEqual(critical, "CRITICAL")

class TestEventModel(StashboardTest):
    pass


class TestStatusModel(StashboardTest):

    def test_invalid_status_slug(self):
        """ An invalid service slug shoud cause Service.get_by_slug to
        return None.
        """
        fetched = models.Status.get_by_slug("doesntexists")
        self.assertEqual(fetched, None) 
