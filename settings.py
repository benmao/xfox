#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/5 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import os
DEBUG = True

#settings for google storage
gs_access_key_id =""
gs_secret_access_key=""
cname ="http://g.xfox.us"
bucket_name = "g.xfox.us"

#role
ROLE= {
    'B':['Banned','Banned User'],
    'M':['Member','Member User'],
    'A':['Administrator','Administrator'],
    'G':['Guest','Guest'],
}

#xFox Setting

class Setting():
    title = "xFox"
    description = u"xFox -变异的狐狸"
    key_words = u"xFox"
    
    domain = "http://xfox.appspot.com"
    timedelta = 0.8
    version = "0.1.2"
    


    
#OpenID Provider
OPENID = (
    ('Gmail','gmail.com'),
    ('MyOpenID','myopenid.com'),
)
if __name__=='__main__':
    pass