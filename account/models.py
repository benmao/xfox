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
    def put(self):
        if not self.is_saved():
            self.name_lower = self.name.lower()
            self.email = self.email.lower()
            self.user_id = Counter.get_max("user").value
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
    
class Role(db.Model):
    pass

    
if __name__=='__main__':
    pass