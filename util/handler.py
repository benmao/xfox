#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import os
import logging
import traceback
import sys
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.http import parse_cookie
from account.models import Session
from google.appengine.api import users
from discussion.models import Tag
import re
from dash.models import Counter
from util.wsgi import RequestHandler
from util.decorator import mem
from django.utils import simplejson
import settings

webapp.template.register_template_library('util.filter')
webapp.template.register_template_library('util.cache')


class NotFound(Exception):
    pass

class Forbidden(Exception):
    pass


def get_or_404(func,*args,**kwargs):
    obj = func(*args,**kwargs)
    if obj is None:
        raise NotFound()
    return obj

class FeedHandler(webapp.RequestHandler):
    def initialize(self,request,response):
        webapp.RequestHandler.initialize(self,request,response)
        self.template_value = {}
        self.setting = settings.Setting()
        self.template_value['setting'] = self.setting
        
    def render(self,template_file):
        template_file = "themes/default/%s" % (template_file)
        path = os.path.join(os.path.dirname(__file__), r'../',template_file)
        self.response.headers['Content-Type']='application/atom+xml'
        self.response.out.write(template.render(path, self.template_value))

class PublicHandler(webapp.RequestHandler):
    
    def initialize(self,request,response):
        '''
        init webapp.RequestHandler
        '''
        webapp.RequestHandler.initialize(self,request,response)
        
    
        self.setting = settings.Setting()
        self.template_value={'setting':self.setting}
        
        #handler xfox-session-key
        cookies = parse_cookie(self.request.headers.get("Cookie",""))
        self.session_key = cookies.get('xfox-session-key',None)
        
        logging.info("session_key:%s" % (self.session_key))
        
        self.user = None
        self.role = ['G'] #Guest User
        if not self.session_key is None and len(self.session_key)==32:
            self.user = Session.get_user_by_session(self.session_key)
            if not self.user is None:
                self.role = self.user.role
        self.template_value['user']=self.user
        self.template_value['role']=self.role
       
        #handler os
        self.os = 'default' #html5
        user_agent = self.request.headers.get("User-Agent",'')
        #if "MSIE" in user_agent:
            #self.os = 'ie'
            
        #handler not endswith /
        self.template_value['os']=self.os 
        if not self.request.path.endswith("/"):
            return self.redirect(self.request.path+"/",True)
        
        self.p = self.request.path.lower() #path
        
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
        self.response.out.write(self.get_render(template_file))
        
    def get_render(self,template_file):
        template_file = "themes/%s/%s" % (self.os,template_file)
        path = os.path.join(os.path.dirname(__file__), r'../',template_file)
        return template.render(path, self.template_value)
        
    def json(self,data):
        self.response.headers['Content-Type']='application/json'
        #handler utf-8
        for key in data:
            if isinstance(data[key],(str)):
                data[key]=data[key].decode('utf-8')
        self.response.out.write(simplejson.dumps(data))
        
        
    def error(self,code):
        self.response.clear()
        self.response.set_status(code)
        if code ==404:
            self.render("404.html")
        elif code ==403:
            self.render("403.html")
        elif code == 500:
            self.render("500.html")
            
    def handle_exception(self, exception, debug_mode):
        if isinstance(exception,NotFound):
            return self.error(404)
        elif isinstance(exception,Forbidden):
            return self.error(403)
        else:
            self.error(500)
            logging.exception(exception)
            if debug_mode:
                lines = ''.join(traceback.format_exception(*sys.exc_info()))
                self.response.clear()
                self.response.out.write('<pre>%s</pre>' % (cgi.escape(lines, quote=True)))
            
class PublicWithSidebarHandler(PublicHandler):
    def initialize(self,request,response):
        PublicHandler.initialize(self,request,response)
        self.template_value['tags']=Tag.get_all()
        
class AdminHandler(webapp.RequestHandler):
    def initialize(self,request,response):
        webapp.RequestHandler.initialize(self,request,response)
        self.setting = settings.Setting()
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
        self.setting = settings.Setting()
        
if __name__=='__main__':
    pass