#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import logging

from google.appengine.api import memcache

#decorator for get data from memcache
def mem(key, time=60):
    def decorator(fxn):
        def wrapper(*args, **kwargs):
            data = memcache.get(key)
            if data is  None:
                data = fxn(*args, **kwargs)
                logging.info("get data from db,key:%s" % key)
                memcache.set(key, data, time)
            return data
        return wrapper
    return decorator

if __name__=='__main__':
    pass