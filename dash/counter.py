#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/10 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from google.appengine.ext import db
from util.decorator import mem,delmem
from google.appengine.api import memcache
import random

class ShardCount(db.Model):
    name = db.StringProperty(required = True)
    count = db.IntegerProperty(required=True,default=0)
    model_type = db.StringProperty(indexed=True)
    date = db.DateTimeProperty(auto_now = True)
    
    @classmethod
    def get_increment_count(cls,name,model_type,num=1):
        count = ShardCount.get_count(name)
        ShardCount.increment(name,model_type,num)
        return count + num
    
    @classmethod
    def get_count(cls,name):
        @mem(name,60*10)
        def _get_count(name):
            total = 0
            for counter in  ShardCount.all().filter('name =',name):
                total +=counter.count
            return total
        return _get_count(name)
    
    @classmethod
    def set_count(cls,name,num):
        @delmem(name)
        def _set_count(name,num):
            sharecounts = ShardCount.all().filter('name =',name).fetch(30)
            for sharecount in sharecounts:
                sharecount.count =0
                sharecount.put()
                
            if sharecounts :
                sharecounts[0].count = num
                sharecounts[0].put()
        return _set_count(name,num)

    @classmethod
    def decrement(cls,name,num=1):
        t = num
        def txn(num):
            sharecounts = ShardCount.all().filter('name =',name).order('count').fetch(30)
            for sharecount in sharecounts:
                if sharecount.count >= num:
                    sharecount.count -= num
                    sharecount.put()
                    return 
                num -= sharecount.count
                sharecount.count = 0
                sharecount.put()
        txn(num)
        memcache.decr(name,t)
    
    @classmethod
    def increment(cls,name,model_type,num=1):
        '''
        name  like  disviews:keyid:1
        '''
        def txn():
            index = random.randint(0,20)
            key_name = '%s:%s' % (name,index)
            counter = ShardCount.get_by_key_name(key_name)
            if counter is None:
                counter = ShardCount(key_name =key_name,name = name,model_type=model_type)
            counter.count += num
            counter.put()
        db.run_in_transaction(txn)
        memcache.incr(name,num)
        

if __name__=='__main__':
    pass