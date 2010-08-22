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
from account.models import User,Mention,UserFollow,Session
from util.base import *
from discussion.models import Discussion,Comment,Bookmark,RecentCommentLog,DiscussionFollow
from util.decorator import requires_login, json_requires_login,openid_requires_login,https_requires
from util.wsgi import webapp_add_wsgi_middleware
from google.appengine.api import users
from google.appengine.api import memcache

class A():
    def __init__(self,key,value):
        self.key = key
        self.value = value

def dict2obj(dic):
    if dic is None:
        return None
    return [ A(key,value) for key,value in dic.items()]

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
        if not self.user is None: #have logined
            self.redirect("/")
        self.template_value['go'] = self.request.get("go")
        self.render("signin.html")
    
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
        self.response.headers['Set-Cookie'] ='xfox-session-key=;path=/'
        logging.info(self.user.logout_type)
        if self.user.logout_type == "openid":
            return self.redirect(users.create_logout_url("/"))
        #Notice : need remove sessionid from Session DB.
        #Session.remove(self.session_key)
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
        self.template_value['f_tag'] = {'key':"u/%s" % u.name_lower,'title':u.name,'show': True} 
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
        
class OpenIDAddHandler(PublicHandler):
    @openid_requires_login
    @requires_login
    def get(self):
        openid_user = users.get_current_user()
        self.template_value['openid_user'] = openid_user
        self.template_value['logout_url'] = users.create_logout_url('/a/setting/')
        self.render("openid_add.html")

    @openid_requires_login
    @requires_login
    def post(self):
        openid_user = users.get_current_user()
        result,error=User.add_openid(self.user.name,openid_user.federated_identity(),openid_user.user_id())
        if not result:
            self.template_value['error']=error
            self.template_value['logout_url'] = users.create_logout_url('/a/setting/')
            return self.render("openid_add.html")
        memcache.delete(self.session_key)
        self.redirect("/a/setting/")
        
class OpenIDRemoveHandler(PublicHandler):
    @requires_login
    def get(self):
        openid_id = self.request.get("id")
        User.remove_openid(self.user.name,openid_id)
        memcache.delete(self.session_key) 
        self.redirect("/a/setting/")
            
class UserSettingHandler(PublicHandler):
    @requires_login
    def get(self):
        self.template_value['openids']= dict2obj(self.user.openid_dict)
        self.render("setting.html")
        
class UserSettingPwdHandler(PublicHandler):
    @requires_login
    def post(self):
        oldpwd = self.request.get("oldpwd")
        pwd = self.request.get("pwd")
        
        result,info = User.update_pwd(self.user.email,oldpwd,pwd)
        self.template_value['pwd_error']=info
        self.render("setting.html")
        
            
class UserNotAllowedHandler(PublicHandler):
    def get(self):
        self.render("not_allow.html")
        
class DiscussionCloseHandler(PublicHandler):
    @json_requires_login
    def post(self):
        key = self.request.get("key")
        dis = Discussion.get(key)
        if dis is None:
            return self.json({"error":u"请不要干坏事哈"})
        if dis.user_name != self.user.name:
            return self.json({"error":u"再干坏事就打PP"})
        dis.is_closed = True
        dis.put()
        return self.json({"result":True})
    
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
                                                      ('/a/openid/signup/',OpenIDSignUpHandler),
                                                      ('/a/openid/add/',OpenIDAddHandler),
                                                      ('/a/openid/remove/',OpenIDRemoveHandler),
                                                      ('/a/mention/',UserMentionHandler),
                                                      ('/a/mention/read/',UserMentionReadHandler),
                                                      ('/a/remind/',UserRemindHandler),
                                                      ('/a/follow/', UserFollowIndexHandler),
                                                      ('/a/followread/',UserFollowReadHandler),
                                                      ('/a/discussion/close/',DiscussionCloseHandler),
                                                      ('/a/setting/',UserSettingHandler),
                                                      ('/a/setting/pwd/',UserSettingPwdHandler),
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
