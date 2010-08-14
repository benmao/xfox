#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from google.appengine.ext import db
from util.decorator import mem,delmem
from util.base import Base36
    
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
       
class MemcacheStatus(db.Model):
    hits = db.IntegerProperty(default=0)
    misses = db.IntegerProperty(default=0)
    items = db.IntegerProperty(default=0)
    bytes = db.IntegerProperty(default=0)
    created = db.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def new(cls,hits,misses,items,bytes):
        obj = MemcacheStatus(hits = hits,misses = misses,items = items,bytes = bytes)
        obj.put()
        
    @classmethod
    def get_recent_24(cls):
        return MemcacheStatus.all().order('-created').fetch(24*6)
        
if __name__=='__main__':
    pass