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

# API HANDLER
import wsgiref.handlers

from google.appengine.ext import webapp
from stashboard.handlers import api

ROUTES = [
    #API
    (r'/api/(.+)/services', api.ServicesListHandler),
    (r'/api/(.+)/services/(.+)/events', api.EventsListHandler),
    (r'/api/(.+)/services/(.+)/events/current', api.CurrentEventHandler),
    (r'/api/(.+)/services/(.+)/events/(.+)', api.EventInstanceHandler),
    (r'/api/(.+)/services/(.+)', api.ServiceInstanceHandler),
    (r'/api/(.+)/statuses', api.StatusesListHandler),
    (r'/api/(.+)/statuses/(.+)', api.StatusInstanceHandler),
    (r'/api/(.+)/status-images', api.ImagesListHandler),
    (r'/api/(.+)/levels', api.LevelsListHandler),
    (r'/api/.*', api.NotFoundHandler),
]

def application():
    return webapp.WSGIApplication(ROUTES)

def main():
    wsgiref.handlers.CGIHandler().run(application())

if __name__ == "__main__":
    main()
