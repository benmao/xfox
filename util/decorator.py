#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import logging

from google.appengine.api import memcache
from functools import wraps
from google.appengine.api import users

#decorator for get data from memcache
def mem(key, time=3600):
    def decorator(fxn):
        def wrapper(*args, **kwargs):
            data = memcache.get(key)
            if data is  None:
                data = fxn(*args, **kwargs)
                logging.info("get data from db,key:%s" % key)
                memcache.set(key, data, time)
            else:
                logging.info("get data from memcache :%s" % key)
            return data
        return wrapper
    return decorator

def delmem(*keys):
    def decorator(fnx):
        def wrapper(*args,**kwargs):
            return fnx(*args,**kwargs)
        for key in  keys:
            memcache.delete(key)
            logging.info("del mem key :%s" % key)
        return wrapper
    return decorator

def requires_login(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.user is None:
            return method(self,*args,**kwargs)
        return self.redirect("/a/signin/?go=%s" % self.request.url)
    return wrapper

def openid_requires_login(method):
    @wraps(method)
    def wrapper(self,*args,**kwargs):
        if  users.get_current_user():
            return method(self,*args,**kwargs)
        return self.redirect("/_ah/login_required?go=%s" % self.request.url)
    return wrapper
            

def json_requires_login(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.user is None:
            return method(self,*args,**kwargs)
        return self.json({"error":"Need Login"})
    return wrapper

if __name__=='__main__':
    pass