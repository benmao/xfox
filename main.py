#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from dash.models import Counter
from util.handler import PublicHandler,PublicWithSidebarHandler
from util.decorator import requires_login
from discussion.models import Tag,Discussion
from util.base import *
from dash.models import Counter,MemcacheStatus
from account.models import User
import settings
from util.wsgi import webapp_add_wsgi_middleware
from google.appengine.api import memcache

class MainHandler(PublicWithSidebarHandler):

    #@requires_login
    def get(self):
        self.template_value['diss'] = Discussion.get_recent()
        self.render('index.html')
    
class UpdateHandler(PublicHandler):
    def get(self):
        for user in User.all():
            user.login_type = ['pwd']
            user.openid_id = []
            user.identity = []
            user.put()
            
class MemcacheHandler(PublicHandler):
    def get(self):
        mems = MemcacheStatus.get_recent_24()
        self.template_value['mem'] = memcache.get_stats()
        self.template_value['rates']=','.join([str(obj.hits*100.0/(obj.hits+obj.misses))for obj in mems ])
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
