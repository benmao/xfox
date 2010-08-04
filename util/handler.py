#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class PublicHandler(webapp.RequestHandler):
    
    def initialize(self,request,response):
        '''
        init webapp.RequestHandler
        '''
        webapp.RequestHandler.initialize(self,request,response)
        self.template_value={}
        
    def render(self, template_file):
        '''
        render template for desktop and mobile
        '''
        template_file = "themes/default/%s" % (template_file)
        path = os.path.join(os.path.dirname(__file__), r'../',template_file)
        self.response.out.write(template.render(path, self.template_value))


if __name__=='__main__':
    pass