#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import logging
import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from  util.handler import PublicHandler
import settings
from account.models import User
from util.base import *

class SignUpHandler(PublicHandler):
    def get(self):
        self.render("signup.html")
    
    def post(self):
        email = self.request.get("email").strip()
        name = self.request.get("name").strip()
        pwd = self.request.get("pwd").strip()
        
        funclist = [
            (check_email,email,'email_error',u"邮箱格式不对"),
            (check_name,name,'name_error',u"用户名格式不对,[a-z,0-9]{3,16}"),
            (User.check_email,email,'email_error',u"邮箱已经存在"),
            (User.check_name,name,'name_error',u"用户名已经存在"),
            (check_pwd,pwd,'pwd_error',u"密码长度6-16"),
        ]
        
        for func, var,error_name,error in  funclist:
            if not func(var):
                self.template_value[error_name] = error
                self.template_value['name']=name
                self.template_value['pwd']=pwd
                self.template_value['email']=email
                return self.render("signup.html")
            
        User.new(email,name,pwd)
        #login user
        self.redirect("/a/signin/")
        
class SignInHandler(PublicHandler):
    def get(self):
        self.render("signin.html")
    
    def post(self):
        email = self.request.get("email").strip()
        pwd = self.request.get("pwd").strip()
        
        user,session = User.login(email,pwd)
        if user and session:
            d = datetime.datetime.now()+datetime.timedelta(days =30)
            self.response.headers['Set-Cookie'] = "xfox-session-key=%s;path=/;expires=%s" % (session.key().name(),get_gmt(d))
            self.redirect("/")
        self.template_value['error'] =u"邮箱或密码不正确"
        self.render("signin.html")
        
class SignOutHandler(PublicHandler):
    def get(self):
        self.response.headers['Set-Cookie'] ='xfox-session-key="";path=/'
        self.redirect("/")
        
def main():
    application = webapp.WSGIApplication(
                                                     [('/a/signup/',SignUpHandler),
                                                      ('/a/signin/',SignInHandler),
                                                      ('/a/signout/',SignOutHandler),
                                                         ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
