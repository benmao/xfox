#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from dash.models import Setting
from django.http import parse_cookie
from account.models import Session
from google.appengine.api import users
from discussion.models import Tag
import re
from dash.models import Counter

webapp.template.register_template_library('util.filter')

class PublicHandler(webapp.RequestHandler):
    
    def initialize(self,request,response):
        '''
        init webapp.RequestHandler
        '''
        webapp.RequestHandler.initialize(self,request,response)
        
        
        self.setting = Setting.get_setting()
        self.template_value={'setting':self.setting}
        
        #handler xfox-session-key
        cookies = parse_cookie(self.request.headers.get("Cookie",""))
        self.session_key = cookies.get('xfox-session-key',None)
        
        logging.info("session_key:%s" % (self.session_key))
        
        self.user = None
        if not self.session_key is None and len(self.session_key)==32:
            self.user = Session.get_user_by_session(self.session_key)
        self.template_value['user']=self.user
        
        user_agent = self.request.headers.get("User-Agent",'')
        
        
    def is_ajax(self):
        '''
        http://code.djangoproject.com/attachment/ticket/6616/is_ajax.diff
        '''
        return "X-Requested-With" in self.request.headers and \
               self.request.headers['X-Requested-With'] == "XMLHttpRequest"
        
    def render(self, template_file):
        '''
        render template for desktop and mobile
        '''
        template_file = "themes/default/%s" % (template_file)
        path = os.path.join(os.path.dirname(__file__), r'../',template_file)
        self.response.out.write(template.render(path, self.template_value))
        
    def error(self,code):
        #handler not endswith /
        if not self.request.path.endswith("/"):
            return self.redirect(self.request.path+"/",True)
        
        self.response.set_status(code)
        if code ==404:
            self.render("404.html")
        elif code ==403:
            self.render("403.html")
            
class PublicWithSidebarHandler(PublicHandler):
    def initialize(self,request,response):
        PublicHandler.initialize(self,request,response)
        self.template_value['tags']=Tag.get_all()
        self.template_value['count_user'] = Counter.get_count("user").value
        self.template_value['count_discussion'] = Counter.get_count("discussion").value
        self.template_value['count_comment'] = Counter.get_count("comment").value
    
class AdminHandler(webapp.RequestHandler):
    def initialize(self,request,response):
        webapp.RequestHandler.initialize(self,request,response)
        self.setting = Setting.get_setting()
        self.template_value={'setting':self.setting}
        
        #make ture login as admin
        user = users.get_current_user()
        if not user:
            return  self.redirect(users.create_login_url(self.request.uri))
        if users.is_current_user_admin():
            return self.error(403)
        
    def render(self,template_file):        template_file = "dash/views/%s" % (template_file)
        path = os.path.join(os.path.dirname(__file__), r'../',template_file)
        self.response.out.write(template.render(path, self.template_value))
        
class TaskHandler(webapp.RequestHandler):
    def initialize(self,request,response):
        webapp.RequestHandler.initialize(self,request,response)
        
if __name__=='__main__':
    pass