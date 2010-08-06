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
    is_draft = db.BooleanProperty(default =False)
    
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
        return Category.all().filter("is_draft =",False)
    
    @classmethod
    def get_draft(cls):
        return Category.all().filter("is_draft =",True)
    
    @classmethod
    def get_category(cls,slug):
        return Category.all().filter("slug =",slug).get()
    
    @classmethod
    def draft(cls,slug):
        cat = Category.get_category(slug)
        if not cat is None:
            cat.is_draft= True 
            cat.put()
            
    @classmethod
    def un_draft(cls,slug):
        cat = Category.get_category(slug)
        if not cat is None:
            cat.is_draft= False
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
    is_draft = db.BooleanProperty(default =False)
    
    def put(self):
        if not self.is_saved(): #create
            self.category.count_tag +=1
            self.category.put() #add category tag count
        super(Tag,self).put()
        
    def delete(self):
        self.category.count_tag -=1
        self.category.put()
        self.is_draft=True
        self.put() # set is_draft 
        
    @property
    def slug(self):
        return self.key().name()
        
    @property
    def url(self):
        return '/%s/' % self.key().name()
    
    @classmethod
    def get_all(cls):
        return Tag.all().filter("is_draft =",False)
    
    @classmethod
    def get_draft(cls):
        return Tag.all().filter("is_draft =",True)
    
    @classmethod
    def check_slug(cls,slug):
        return Tag.get_by_key_name(slug)
    
    @classmethod
    def get_tag_by_slug(cls,slug):
        return Tag.get_by_key_name(slug)
    
    @classmethod
    def new(cls,slug,title,key_words,description,category):
        '''
        Notice:http://code.google.com/intl/en/appengine/docs/python/datastore/keysandentitygroups.html
        '''
        slug = filter_url(slug)
        tag = Tag.check_slug(slug)
        if  tag is None:
            tag = Tag(key_name = slug)
        tag.title=title
        tag.key_words=key_words
        tag.description=description
        tag.category = Category.get(category)
        tag.put()
        return tag
    
    @classmethod
    def draft(cls,slug):
        tag = Tag.get_tag_by_slug(slug)
        if not tag is None:
            tag.is_draft = True
            tag.put()
            
    @classmethod
    def un_draft(cls,slug):
        tag = Tag.get_tag_by_slug(slug)
        if not tag is None:
            tag.is_draft = False
            tag.put()
            
class Discussion(db.Model):
    tag = db.ReferenceProperty(Tag)
    tag_title = db.StringProperty()
    slug = db.StringProperty()
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
    is_draft = db.BooleanProperty(default =False)
    
    f = db.StringProperty() #format type
    is_closed = db.BooleanProperty(default = False)

    
if __name__=='__main__':
    pass