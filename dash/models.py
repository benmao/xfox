#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from google.appengine.ext import db
from util.decorator import mem,delmem
from util.base import Base36

class Setting(db.Model):
    title = db.StringProperty(default ='xFox')
    description = db.TextProperty()
    key_words = db.StringProperty()
    
    domain = db.StringProperty()
    timedelta = db.FloatProperty(default =8.0)
    version = "0.0.5"
    
    @delmem("setting") 
    def put(self):
        super(Setting,self).put()
        
    @classmethod
    @mem("setting")
    def get_setting(cls):
        setting = cls.get_by_key_name("default")
        if setting is None:
           #init setting
            setting = Setting(key_name="default")
            setting.title = 'xFox'
            setting.domain = 'http://localhost'
            setting.put()
        return setting
    
class Counter(db.Model):
    name = db.StringProperty(required=False)
    value = db.StringProperty(default ='0') #use base36
    created = db.DateTimeProperty(auto_now_add =True)
    last_updated = db.DateTimeProperty(auto_now = True)
    
    def put(self):
        self.name = self.key().name()
        super(Counter,self).put()
    
    @classmethod
    def get_count(self,key_name):
        obj = Counter.get_by_key_name(key_name) 
        if obj is None:
            obj = Counter(key_name = key_name)
            obj.value='0'
        return obj
    
    @classmethod
    def get_count_base(cls,key_name):
        return int(Counter.get_count(key_name).value,36)
    
    @classmethod
    def get_max(self,key_name):
        '''
        return max value +1
        '''
        obj = Counter.get_count(key_name)
        obj.value = Base36(obj.value)+1
        obj.put()
        return obj
       
if __name__=='__main__':
    pass