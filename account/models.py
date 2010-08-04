#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from google.appengine.ext import db 

from util.base import *
import datetime

class User(db.Model):
    name = db.StringProperty(required=True)
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
    
    def put(self):
        self.name_lower = self.name.lower()
        self.email = self.email.lower()
        super(User,self).put()
    
    #classmethod
    
    @classmethod
    def check_name(cls,name):
        return User.all().filter("name_lower =",name.lower).get()
    
    @classmethod
    def check_email(cls,email):
        return User.all().filter("email =",email).get()
    
    @classmethod
    def new(cls,email,name,pwd):
        if cls.check_email(name) is None and cls.check_name(name) is None:
            secret_key,pwd = encrypt_pwd(pwd) 
            user = cls(email =email,name=name,secret_key=secret_key,pwd = pwd)
            user.put()
            return user
        return None
    
    @classmethod
    def login(cls,email,pwd):
        pass
    
class Invitation(db.Model):
    email = db.StringProperty()
    exp_date = db.DateTimeProperty()
    
    
    @property
    def key_name(self):
        return self.key().name()
    
    #classmethod
    @classmethod
    def  new(cls,email):
        invition = Invitation.all().filter("email =",email).get()
        if not invition is None:
            return  invition
        
        invition = Invitation(key_name = random_md5(email))
        invition.email = email
        invition.exp_date = datetime.datetime.now() + datetime.timedelta(days =3)
        invition.put()
        return invition
        
    @classmethod
    def check_invitation(cls,key_name):
        return Invitation.all().filter('key_name =',key_name).filter('exp_date <',datetime.datetime.now()).get()
    
class Session(db.Model):
    user = db.ReferenceProperty(user)
    exp_date = db.DateTimeProperty()
    
if __name__=='__main__':
    pass