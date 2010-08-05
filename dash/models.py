#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from google.appengine.ext import db
from util.decorator import mem,delmem

class Setting(db.Model):
    title = db.StringProperty(default ='xFox')
    description = db.TextProperty()
    key_words = db.StringProperty()
    
    domain = db.StringProperty()
    timedelta = db.FloatProperty(default =8.0)
    version = "0.0.1"
    
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
    
if __name__=='__main__':
    pass