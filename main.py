#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from util.handler import PublicHandler,PublicWithSidebarHandler
from util.decorator import requires_login
from discussion.models import Tag,Discussion
import settings

class MainHandler(PublicWithSidebarHandler):

    #@requires_login
    def get(self):
        self.render('index.html')
    
class UpdateHandler(PublicHandler):
    def get(self):
        diss = Discussion.all()
        for dis in diss:
            dis.last_comment = dis.created
            dis.put()
class NotFoundHandler(PublicHandler):
    def get(self):
        self.error(404)
        
    def post(self):
        self.error(404)
        
def main():
    application = webapp.WSGIApplication([
                                        ('/', MainHandler),
                                        ('/e/',UpdateHandler),
                                        ('/.*',NotFoundHandler),
                                        ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
