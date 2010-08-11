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
import datetime
from dash.models import Counter

class User(db.Model):
    name = db.StringProperty(required=True,indexed=True)
    pwd = db.StringProperty(required = True)
    secret_key =db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    
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
    def put(self):
        if not self.is_saved():
            self.name_lower = self.name.lower()
            self.email = self.email.lower()
            self.user_id = Counter.get_max("user").value
            self.role.append("M")
            self.role.append("G")
        super(User,self).put()
    
    
    @classmethod
    def get_user_by_name(cls,name):
        return User.all().filter("name_lower =",name.lower()).get()
    
    @classmethod
    def check_name(cls,name):
        return User.all().filter("name_lower =",name.lower()).get() is None
    
    @classmethod
    def check_email(cls,email):
        return User.all().filter("email =",email).get() is None
    
    @classmethod
    def new(cls,email,name,pwd):
        secret_key,pwd = encrypt_pwd(pwd) 
        user = cls(email =email,name=name,secret_key=secret_key,pwd = pwd)
        user.put()
        return (0,user)
    
    @classmethod
    def login(cls,email,pwd):
        user = User.all().filter("email =",email).get()
        if user is None:
            return (None,None)
        logging.info("pwd:%s   pwd2:%s" % (user.pwd,encrypt_pwd(pwd,user.secret_key)[1]))
        if user.pwd == encrypt_pwd(pwd,user.secret_key)[1]:
            session = Session.new(user,30) #30days
            return user,session
        return None,None
    
        
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
    exp_date = db.DateTimeProperty()
    
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
            return None if session is None else session.user
        return _get_user_by_session(session_key)
    

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
    
class Role(db.Model):
    name = db.StringProperty(required=True)
    description = db.StringProperty()
    k = db.StringProperty()
    
    @classmethod
    def new(cls,name,description):
        role = Role.all().filter('name =',name).get()
        if role is None:
            role = Role(k=Counter.get_max("role").value, name = name)
        role.name = name
        role.description = description
        role.put()
        
    
if __name__=='__main__':
    pass