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
from discussion.models import Tag,Discussion,Comment,Bookmark
from util.base import *
from dash.models import Counter,MemcacheStatus
from account.models import User
import settings
from util.wsgi import webapp_add_wsgi_middleware
from google.appengine.api import memcache

def clone_entity(e, **extra_args):
    """Clones an entity, adding or overriding constructor attributes.
    
    The cloned entity will have exactly the same property values as the original
    entity, except where overridden. By default it will have no parent entity or
    key name, unless supplied.
    
    Args:
      e: The entity to clone
      extra_args: Keyword arguments to override from the cloned entity and pass
        to the constructor.
    Returns:
      A cloned, possibly modified, copy of entity e.
    """
    klass = e.__class__
    props = dict((k, v.__get__(e, klass)) for k, v in klass.properties().iteritems())
    props.update(extra_args)
    return klass(**props)

class MainHandler(PublicWithSidebarHandler):

    #@requires_login
    def get(self):
        self.template_value['diss'] = Discussion.get_recent()
        self.render('index.html')
    
class UpdateHandler(PublicHandler):
    def get(self):
        user = User.get_user_by_name('ben')
        user.role.append('A')
        print user.role
        user.put()
            
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
