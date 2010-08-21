#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/11 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import urllib
import settings
import logging

from util.handler import TaskHandler
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from discussion.models import DiscussionFollow
from gs.models import LatexImage
from account.models import UserFollow,User
from google.appengine.api import urlfetch

class DiscussionFollowHandler(TaskHandler):
    def get(self):
        user = User.get_user_by_name("ccc") 
        users = UserFollow.get_follower(user)
        for x in users:
            print x.name
       
    def post(self):
        dis = self.request.get("dis")
        DiscussionFollow.new(dis)
        
    
class LatexHandler(TaskHandler):
    def post(self):
        latex_str = self.request.get("latex_str")
        md5_str = self.request.get("md5_str")
        LatexImage.new(latex_str,md5_str)
        
class HubBubHandler(TaskHandler):
    def get(self):
        self.post()
    
    def post(self):
        data = urllib.urlencode({
        'hub.url': '%s/f/' % (self.setting.domain,),
        'hub.mode': 'publish', 
        })
        response = urlfetch.fetch(self.setting.hubbub_hub_url, data, urlfetch.POST)
        if response.status_code != 200:
            raise Exception("Hub ping failed", response.status_code, response.content)
        else:
            logging.info("%s/f/  hubbub success!" % (self.setting.domain,))
                
def main():
    application = webapp.WSGIApplication([
                                        ('/t/d/follow/', DiscussionFollowHandler),
                                        ('/t/d/latex/',LatexHandler),
                                        ('/t/d/hubbub/',HubBubHandler),
                                        ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__=='__main__':
    main()