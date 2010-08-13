#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/10 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from util.handler import TaskHandler
import settings
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import logging
from account.models import Mention,User
from discussion.models import DiscussionVisitLog
from google.appengine.api import memcache

class UserMentionHandler(TaskHandler):
    def get(self):
        pass
    
    def post(self):
        source_url = self.request.get("source_url")
        source_user = self.request.get("source_user")
        user_name = self.request.get("user")
        logging.info("bbb"+user_name)
        user = User.get_user_by_name(user_name)
        logging.info("aaa"+user.name)
        if not user is None:
            Mention.new(user,source_url,source_user)
            
class DiscussionVisitLogHandler(TaskHandler):
    def get(self):
        logs = memcache.get(":visitlogs:",set([]))
        for log in logs: #log like ben/asf-sdf/sdfsf/
            user_name,tag_key,dis_key = log.split('/')[0:3]
            DiscussionVisitLog.new(user_name,tag_key,dis_key)
        logging.info("write %s log" % len(logs))
        memcache.set(":visitlogs:",set([]),3600)
        
def main():
    application = webapp.WSGIApplication([
                                        ('/t/u/mention/', UserMentionHandler),
                                        ('/t/u/logs/',DiscussionVisitLogHandler),
                                        
                                        ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__=='__main__':
    main()