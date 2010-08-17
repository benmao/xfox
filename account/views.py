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
from  util.handler import PublicHandler,PublicWithSidebarHandler
import settings
from account.models import User,Mention,UserFollow
from util.base import *
from discussion.models import Discussion,Comment,Bookmark,RecentCommentLog,DiscussionFollow
from util.decorator import requires_login, json_requires_login,openid_requires_login,https_requires
from util.wsgi import webapp_add_wsgi_middleware
from google.appengine.api import users

class SignUpHandler(PublicHandler):
    @https_requires
    def get(self):
        self.render("signup.html")
    
    @https_requires
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
    @https_requires
    def get(self):
        if not self.user is None: #have logined
            self.redirect("/")
        self.template_value['go'] = self.request.get("go")
        self.render("signin.html")
    
    @https_requires
    def post(self):
        email = self.request.get("email").strip()
        pwd = self.request.get("pwd").strip()
        go = self.request.get("go").strip()
        
        user,session = User.login(email,pwd)
        if user and session:
            d = datetime.datetime.now()+datetime.timedelta(days =30)
            self.response.headers['Set-Cookie'] = "xfox-session-key=%s;path=/;expires=%s" % (session.key().name(),get_gmt(d))
            self.redirect(go) if go else self.redirect("/")
        self.template_value['error'] =u"邮箱或密码不正确"
        self.render("signin.html")
        
class SignOutHandler(PublicHandler):
    def get(self):
        self.response.headers['Set-Cookie'] ='xfox-session-key=;ACSID=;path=/'
        self.redirect("/")

class UserProfileHandler(PublicWithSidebarHandler):
    def get(self,name):
        u = User.get_user_by_name(name)
        if u is None:
            return self.error(404)
        self.template_value['u']=u
        self.template_value['is_following']=UserFollow.is_following(self.user,name)
        self.template_value['recent_dis']= Discussion.get_recent_dis(u)
        self.template_value['recent_comment'] = RecentCommentLog.get_recent_comment(u)
        self.template_value['recent_bookmark']= Bookmark.get_recent_bookmark(u)
        self.render('user.html')
        
class UserMentionHandler(PublicWithSidebarHandler):
    @requires_login
    def get(self):
        self.template_value['mentions']= Mention.get_mention_by_user(self.user)
        self.render('mention.html')
        
class UserMentionReadHandler(PublicHandler):
    @json_requires_login
    def post(self):
        key = self.request.get("key")
        Mention.set_read(key)
        self.json({"result":True})
        
class UserMentionCheckHandler(PublicHandler):
    @requires_login
    def get(self):
        self.response.out.write(Mention.check_mentin(self.user))
        
    @json_requires_login
    def post(self):
        self.json({"count":Mention.check_mentin(self.user)})
        
class UserRemindHandler(PublicHandler):
    @requires_login
    def get(self):
        self.response.out.write("remind")
        
    @json_requires_login
    def post(self):
        self.json({'mention':Mention.check_mentin(self.user),'follow':DiscussionFollow.check_follow(self.user)})
        
class UserFollowIndexHandler(PublicWithSidebarHandler):
    @requires_login
    def get(self):
        self.template_value['follows'] = DiscussionFollow.get_dis_by_user(self.user)
        self.render("follow.html")
        
class UserFollowHandler(PublicWithSidebarHandler):
    @requires_login
    def get(self,name):
        UserFollow.add_follow(self.user,name)
        self.redirect("/u/%s/" % name)
        
class UserFollowReadHandler(PublicHandler):
    @json_requires_login
    def post(self):
        key = self.request.get("key")
        DiscussionFollow.set_read(key)
        return self.json({"result":True})
        
class UserUnFollowHandler(PublicWithSidebarHandler):
    @requires_login
    def get(self,name):
        UserFollow.unfollow(self.user,name)
        self.redirect("/u/%s/" % name)
        
        
class OpenIDSignInHandler(PublicHandler):
    @openid_requires_login
    def get(self):
        go = self.request.get("go","/")
        if not self.user is None:
            self.redirect("/")
        openid_user = users.get_current_user()
        user,session = User.openid_login(openid_user.user_id())
        if user and session:
            d = datetime.datetime.now()+datetime.timedelta(days =30)
            self.response.headers['Set-Cookie'] = "xfox-session-key=%s;path=/;expires=%s" % (session.key().name(),get_gmt(d))
            return self.redirect(go)
        #need reg
        self.redirect("/a/openid/signup/")
       
class OpenIDSignOutHandler(PublicHandler):
    def get(self):
        go = self.request.get("go","/")
        self.response.headers['Set-Cookie'] ='ACSID="";path=/'
        self.redirect("/")
        
class OpenIDSignUpHandler(PublicHandler):
    @openid_requires_login
    def get(self):
        openid_user = users.get_current_user()
        self.template_value["name"] =""
        return self.render("openid_signup.html")
      
    @openid_requires_login
    def post(self):
        openid_user = users.get_current_user()
        self.template_value['openid_user']=openid_user
        name = self.request.get("name")
        self.template_value["name"]=name
        if not User.check_email(openid_user.email()):
            self.template_value['email_error'] = u"%s已经存在，请登录后绑定" % openid_user.email()
            return self.render("openid_signup.html")
        if not check_name(name):
            self.template_value["name_error"] = u"%s不符合规定[a-z0-9]{3,16}" % name
            return self.render("openid_signup.html")
        if not User.check_name(name):
            self.template_value["name_error"] = u"%s已经存在，请更换用户名" % name
            return self.render("openid_signup.html")
        if not User.check_openid_id(openid_user.user_id()):
            self.template_value["id_error"] = u"此OpenID已经绑定过了，请直接登录"
            return self.render("openid_signup.html")
        User.new_by_openid(openid_user.email(),name,openid_user.federated_identity(),openid_user.user_id())
        self.redirect("/a/openid/signin/")
        
class UserNotAllowedHandler(PublicHandler):
    def get(self):
        self.render("not_allow.html")
        
class NotFoundHandler(PublicHandler):
    def get(self):
        self.error(404)
    
    def post(self):
        self.error(404)
def main():
    application = webapp.WSGIApplication(
                                                     [('/a/signup/',SignUpHandler),
                                                      ('/a/signin/',SignInHandler),
                                                      ('/a/signout/',SignOutHandler),
                                                      ('/a/openid/signin/',OpenIDSignInHandler),
                                                      ('/a/openid/signout/',OpenIDSignOutHandler),
                                                      ('/a/openid/signup/',OpenIDSignUpHandler),
                                                      ('/a/mention/',UserMentionHandler),
                                                      ('/a/mention/read/',UserMentionReadHandler),
                                                      ('/a/remind/',UserRemindHandler),
                                                      ('/a/follow/', UserFollowIndexHandler),
                                                      ('/a/followread/',UserFollowReadHandler),
                                                      ('/a/follow/(?P<name>[a-z0-9A-Z]{3,16})/',UserFollowHandler),
                                                      ('/a/unfollow/(?P<name>[a-z0-9A-Z]{3,16})/',UserUnFollowHandler),
                                                      ('/u/(?P<name>[a-z0-9A-Z]{3,16})/',UserProfileHandler),
                                                      ('/a/notallowed/',UserNotAllowedHandler),
                                                      
                                                      ('/.*',NotFoundHandler),
                                                         ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(webapp_add_wsgi_middleware(application))

if __name__ == '__main__':
    main()
