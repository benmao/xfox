#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import settings

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache

from util.base import *
from util.decorator import requires_login
from util.wsgi import webapp_add_wsgi_middleware
from util.handler import PublicHandler,PublicWithSidebarHandler,FeedHandler,SitemapHandler

from dash.models import Counter
from discussion.models import Tag,Discussion,Comment,Bookmark
from dash.models import Counter,MemcacheStatus
from account.models import User


class MainHandler(PublicWithSidebarHandler):

    #@requires_login
    def get(self):
        self.template_value['diss'] = Discussion.get_recent()
        self.template_value['bookmarks'] = Bookmark.all().order('-created').fetch(10)
        self.render('index.html')
    
class UpdateHandler(PublicHandler):
    def get(self):
        self.template_value['haha']={'a':'111','b':'2222'}
        self.render('test.html')
        
class MemcacheHandler(PublicHandler):
    def get(self):
        mems = MemcacheStatus.get_recent_24()
        self.template_value['mem'] = memcache.get_stats()
        self.template_value['rates']=','.join([str(obj.hits*100.0/(obj.hits+obj.misses))for obj in mems[::-1] ])
        self.render("mem.html")
       
    
class NotFoundHandler(PublicHandler):
    def get(self):
        self.error(404)
        
    def post(self):
        self.error(404)
        
def main():
    application = webapp.WSGIApplication ([
                                        ('/', MainHandler),
                                        ('/e/',UpdateHandler),
                                        ('/s/mem/',MemcacheHandler),
                                        ('/.*',NotFoundHandler),
                                        ],
                                         debug=settings.DEBUG)
#    util.run_wsgi_app(application)
    util.run_wsgi_app(webapp_add_wsgi_middleware(application))
if __name__ == '__main__':
    main()
