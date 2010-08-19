#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/13 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from dash.models import MemcacheStatus
from util.handler import AdminHandler
import settings
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache

class MemcacheHandler(AdminHandler):
    def get(self):
        s = memcache.get_stats()
        MemcacheStatus.new(s['hits'],s['misses'],s['items'],s['bytes'])
        print "aaa"
    
class MemcacheRemove(AdminHandler):
    def get(self):
        print memcache.flush_all()
        
def main():
    application = webapp.WSGIApplication([
                                        ('/s/s/memcache/', MemcacheHandler),
                                        ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__=='__main__':
    main()
