#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from google.appengine.ext import db
from util.decorator import *
from util.base import *
from account.models import User


class Category(db.Model):
    '''
    Father of Tag
    '''
    slug = db.StringProperty()
    title = db.StringProperty()
    key_words = db.StringProperty()
    description = db.StringProperty()
    count_tag = db.IntegerProperty(default =0)
    created = db.DateTimeProperty(auto_now_add=True)
    last_updated = db.DateTimeProperty(auto_now=True)
    draft = db.BooleanProperty(default =False)
    
    @classmethod
    def new(cls,slug,title,key_words,description):
        slug = filter_url(slug)
        obj = Category.all().filter("slug =",slug).get()
        if obj is None:
            #add new 
            obj=Category(slug=slug)
        
        #update data
        obj.title = title
        obj.key_words = key_words
        obj.description = description
        obj.put()
        
    @classmethod
    def get_all(cls):
        return Category.all().filter("draft =",False)
    
    @classmethod
    def get_draft(cls):
        return Category.all().filter("draft =",True)
    
    @classmethod
    def get_category(cls,slug):
        return Category.all().filter("slug =",slug).get()
    
    @classmethod
    def draft(cls,slug):
        cat = Category.get_category(slug)
        if not cat is None:
            cat.draft=True
            cat.put()
            
    @classmethod
    def un_draft(cls,slug):
        cat = Category.get_category(slug)
        if not cat is None:
            cat.draft=False
            cat.put()
    
class Tag(db.Model):
    '''
    key().name() is slug 
    '''
    category = db.ReferenceProperty(Category)
    title = db.StringProperty()
    key_words = db.StringProperty()
    description = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_updated = db.DateTimeProperty(auto_now = True)
    count_discussion = db.IntegerProperty(default=0)
    allow_discussion = db.BooleanProperty(default =True)
    allow_comment = db.BooleanProperty(default =True)
    draft = db.BooleanProperty(default =False)
    
class Discussion(db.Model):
    tag = db.ReferenceProperty(Tag)
    tag_key_name = db.StringProperty()
    title = db.StringProperty()
    key_words = db.StringProperty()
    description = db.StringProperty()
    body =db.TextProperty()
    body_formated = db.TextProperty()
    user = db.ReferenceProperty(User)
    user_name = db.StringProperty()
    
    created = db.DateTimeProperty(auto_now_add=True)
    last_update = db.DateTimeProperty(auto_now=True) 
    last_comment_by = db.StringProperty()
    last_commet = db.DateTimeProperty()
   
    count_comment =db.IntegerProperty(default=0)
    count_bookmark=db.IntegerProperty(default=0)
    
    source = db.StringProperty(required=False)
    draft = db.BooleanProperty(default =False)
    
    f = db.StringProperty() #format type
    closed = db.BooleanProperty(default = False)

    
if __name__=='__main__':
    pass