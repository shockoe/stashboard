# The MIT License
# 
# Copyright (c) 2008 William T. Katz
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.


__author__ = 'Kyle Conroy'

import os
import logging
import wsgiref.handlers

# SITE HANDLER

# Force sys.path to have our own directory first, so we can import from it.
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.api import memcache
from google.appengine.ext import webapp

from stashboard import config
from stashboard.handlers import site
from stashboard.models import Status, Setting

ROUTES = [
    ('/*$', site.BasicRootHandler),
    ('/403.html', site.UnauthorizedHandler),
    ('/404.html', site.NotFoundHandler),
    (r'/services/(.+)/(.+)/(.+)/(.+)', site.BasicServiceHandler),
    (r'/services/(.+)/(.+)/(.+)', site.BasicServiceHandler),
    (r'/services/(.+)/(.+)', site.BasicServiceHandler),
    (r'/services/(.+)', site.ServiceSummaryHandler),
    (r'/documentation/overview', site.DocumentationOverview),
    (r'/documentation/examples', site.DocumentationExamples),
    (r'/documentation/rest', site.DocumentationRest),
    ('/.*$', site.NotFoundHandler),
    
]

def application():
    return webapp.WSGIApplication(ROUTES)

def main():
    # Check if defaults have been installed
    # Keep this for now, will be removed shortly
    installed_defaults = memcache.get("installed_defaults")
    if installed_defaults is None:
        installed_defaults = Setting.all().filter('name = ', 'installed_defaults').get()
        if installed_defaults is None:
            logging.info("Installing default statuses")
            Status.install_defaults()
        if not memcache.add("installed_defaults", True):
            logging.error("Memcache set failed.")

    wsgiref.handlers.CGIHandler().run(application())

if __name__ == "__main__":
    main()
