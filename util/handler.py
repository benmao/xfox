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
            logging.info("ssfddsf:%s" % self.user.email)
        self.template_value['user']=self.user
        
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


if __name__=='__main__':
    pass