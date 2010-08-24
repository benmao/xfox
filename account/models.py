#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import time
import datetime
import logging
from google.appengine.ext import db 

from util.base import  *
from util.decorator import *
from util.db import PickleProperty
from dash.models import Counter

class User(db.Model):
    name = db.StringProperty(required=True,indexed=True)
    pwd = db.StringProperty()
    secret_key =db.StringProperty()
    email = db.StringProperty(required = True)
    email_md5=db.StringProperty()
    
    about = db.StringProperty()
    name_lower = db.StringProperty()
    
    count_visit = db.IntegerProperty(default=0)
    date_first_visit = db.DateTimeProperty(auto_now_add=True)
    date_last_visit = db.DateTimeProperty(auto_now = True)

    count_unread_conversation = db.IntegerProperty(default=0)
    count_discussions = db.IntegerProperty(default=0)
    couont_unread_discussions = db.IntegerProperty(default=0)
    count_comments = db.IntegerProperty(default =0)
    count_drafts = db.IntegerProperty(default =0)
    count_bookmarks = db.IntegerProperty(default =0)
    photo = db.StringProperty()
    
    comment_sort = db.BooleanProperty(default=False)
    user_id = db.StringProperty()
    
    role = db.StringListProperty()
    
    identity = db.StringListProperty()
    openid_id = db.StringListProperty()
    login_type = db.StringListProperty()
    openid_dict = PickleProperty() #dict for openid_id & identity
    
    def put(self):
        if not self.is_saved():
            self.name_lower = self.name.lower()
            self.email = self.email.lower()
            self.email_md5 = get_md5(self.email)
            self.user_id = Counter.get_max("user").value
            self.role.extend(['M','G'])
        super(User,self).put()
    
    @classmethod
    def get_user_by_name(cls,name):
        return User.all().filter("name_lower =",name.lower()).get()
    
    @classmethod
    def check_name(cls,name):
        return User.all().filter("name_lower =",name.lower()).get() is None
    
    @classmethod
    def check_email(cls,email):
        return User.all().filter("email =",email.lower()).get() is None
    
    @classmethod
    def check_openid_id(cls,openid_id):
        return User.all().filter("openid_id =",openid_id).get() is None
    
    @classmethod
    def new(cls,email,name,pwd):
        secret_key,pwd = encrypt_pwd(pwd) 
        user = cls(email =email,name=name,secret_key=secret_key,pwd = pwd)
        user.login_type = ['pwd']
        user.identity = []
        user.openid_id = []
        user.put()
        return user
    
    @classmethod
    def new_by_openid(cls,email,name,identity,openid_id):
        user = User(email = email,name = name)
        user.login_type.append('openid')
        user.identity.append(identity)
        user.openid_id.append(openid_id)
        user.openid_dict = {openid_id:identity}
        user.put()
        return user
    
    @classmethod
    def add_openid(cls,name,identity,openid_id):
        user = User.get_user_by_name(name)
        if not User.check_openid_id(openid_id):
            return False,u"此OpenID已经绑定过，点取消吧！哈哈哈"
        if not 'openid' in user.login_type:
            user.login_type.append('openid')
        user.identity.append(identity)
        user.openid_id.append(openid_id)
        #make true openid_dict is not None
        if user.openid_dict is None:
            user.openid_dict = {}
        user.openid_dict[openid_id] = identity
        user.put()
        return True,u"绑定成功"
        
    @classmethod
    def remove_openid(cls,name,openid_id):
        user = User.get_user_by_name(name)
        logging.info("%s:%s" %(openid_id,user.openid_dict))
        if not openid_id in user.openid_dict:
            return
        user.openid_id.remove(openid_id)
        user.identity.remove(user.openid_dict[openid_id])
        user.openid_dict.pop(openid_id)
        user.put()
        
    @classmethod
    def login(cls,email,pwd):
        user = User.all().filter("email =",email).get()
        if user is None:
            return (None,None)
        if not 'pwd' in user.login_type:
            return (None,None)
        logging.info("pwd:%s   pwd2:%s" % (user.pwd,encrypt_pwd(pwd,user.secret_key)[1]))
        if user.pwd == encrypt_pwd(pwd,user.secret_key)[1]:
            user.logout_type = 'pwd'
            session = Session.new(user,30) #30days
            return user,session
        return None,None
    
    @classmethod
    def openid_login(cls,openid_id):
        user = User.all().filter("openid_id =",openid_id).get()
        if user is None:
            return (None,None)
        user.logout_type = 'openid'
        session = Session.new(user,30)
       
        return user,session
    
    @classmethod
    def update_pwd(cls,email,oldpwd,pwd):
        user = User.all().filter("email =",email.lower()).get()
        if user is None:
            return False,u"用户不存在"
        if not 'pwd' in user.login_type:
            user.secret_key,user.pwd = encrypt_pwd(pwd) 
            user.login_type.append('pwd') #add 'pwd' login_type
            user.put()
            return True,u'密码修改成功，下次登录请使用新密码'
        if user.pwd != encrypt_pwd(oldpwd,user.secret_key)[1]:
            return False,u"旧密码不正确"
        user.secret_key,user.pwd = encrypt_pwd(pwd) 
        user.put()
        return True,u'密码修改成功，下次登录请使用新密码'
        
        
        
class UserFollow(db.Model):
    user = db.ReferenceProperty(User)
    following = db.ListProperty(db.Key)
    following_name = db.StringListProperty()
    
    @classmethod
    def add_follow(cls,user,name):
        name = name.lower()
        if user.name_lower == name:
            return False
        follow = User.get_user_by_name(name)
        if follow is None:
            return False
        user_follow = UserFollow.get_userfollow(user)
        if name in user_follow.following_name:
            return False
        user_follow.following.append(follow.key())
        user_follow.following_name.append(name)
        user_follow.put()
        return True
    
    @classmethod
    def unfollow(cls,user,name):
        name = name.lower()
        follow = User.get_user_by_name(name)
        if follow is None:
            return False
        user_follow = UserFollow.get_userfollow(user)
        if name in user_follow.following_name:
            user_follow.following.remove(follow.key())
            user_follow.following_name.remove(name)
            user_follow.put()
            return True
        return False

    @classmethod
    def get_userfollow(cls,user):
        user_follow = UserFollow.all().filter('user =',user).get()
        if user_follow is None:
            user_follow = UserFollow(user=user)
            user_follow.following=[]
            user_follow.following_name=[]
        return user_follow
        
    @classmethod
    def get_following(cls,user):
        return UserFollow.get_userfollow(user).following
    
    @classmethod
    def get_following_name(cls,user):
        return UserFollow.get_userfollow(user).following_name
    
    @classmethod
    def is_following(cls,user,name):
        return name.lower() in UserFollow.get_following_name(user)
    
    @classmethod
    def get_follower(cls,user):
        return [uf.user for uf in UserFollow.all().filter('following =',user.key()).fetch(100)]
    
class Session(db.Model):
    user = db.ReferenceProperty(User)
    logout_type = db.StringProperty(default="pwd")
    exp_date = db.DateTimeProperty()

    def put(self):
        self.logout_type=self.user.logout_type
        super(Session,self).put()
    
    @classmethod
    def new(cls,user,exp_date =30):
        '''
        session_key:md5(name:time.time()+random_str(6))
        '''
        session_key = random_md5("%s:%s" %(user.name,time.time()))
        logging.info("%s:session_key:%s" % (user.name,session_key))
        session = Session(key_name = session_key,user = user,exp_date=datetime.datetime.now()+datetime.timedelta(days =exp_date))
        session.put()
        return session
    
    @classmethod
    def get_user_by_session(cls,session_key):
        @mem(session_key,3600*24)
        def _get_user_by_session(session_key):
            session = Session.get_by_key_name(session_key)
            if session is None:
                return None
            session.user.logout_type = session.logout_type
            return session.user
        return _get_user_by_session(session_key)
    
    @classmethod
    def remove(cls,session_key):
        session = Session.get_user_by_session(session_key)
        session.exp_date = datetime.datetime.now()
        session.put()
        

class Mention(db.Model):
    user = db.ReferenceProperty(User)
    created = db.DateTimeProperty(auto_now_add=True)
    is_read = db.BooleanProperty(default=False)
    source_url = db.StringProperty()
    source_user = db.StringProperty()
    
    @classmethod
    def new(cls,user,source_url,source_user):
        mention = Mention(user = user,source_url=source_url,source_user=source_user)
        mention.put()
        
    @classmethod
    def get_mention_by_user(cls,user):
        return Mention.all().filter('user =',user).filter('is_read =',False).order('-created').fetch(10)
    
    @classmethod
    def set_read(cls,key):
        mention = Mention.get(key)
        mention.is_read = True
        mention.put()

    @classmethod
    def check_mentin(cls,user):
        return Mention.all().filter('user =',user).filter('is_read =',False).count()
    
if __name__=='__main__':
    pass