#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from util.handler import PublicHandler
from discussion.models import Tag,Discussion
import settings
class TagHandler(PublicHandler):
    def get(self,slug):
        self.response.out.write(slug)

class DiscussionHandler(PublicHandler):
    def get(self,slug,key):
        self.response.out.write("%s:%s" % (slug,key))
        
        
def main():
    application = webapp.WSGIApplication([
                                                          ('/(?P<slug>[a-z0-9-]{2,})/', TagHandler),
                                                          ('/(?P<slug>[a-z0-9-]{2,})/(?P<key>[a-z0-9]+)/',DiscussionHandler),
                                                          ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
