#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/11 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from util.handler import TaskHandler
import settings
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import logging
from discussion.models import DiscussionFollow
from account.models import UserFollow,User
class DiscussionFollowHandler(TaskHandler):
    def get(self):
        user = User.get_user_by_name("ccc") 
        users = UserFollow.get_follower(user)
        for x in users:
            print x.name
       
    def post(self):
        dis = self.request.get("dis")
        DiscussionFollow.new(dis)
        
    
def main():
    application = webapp.WSGIApplication([
                                        ('/t/d/follow/', DiscussionFollowHandler),
                                        ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__=='__main__':
    main()