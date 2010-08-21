#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/20 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import cookielib
import urllib
import urllib2
from threadpool import *

class Poster():
    
    def __init__(self,username,pwd):
        self.username = username
        self.pwd = pwd
        
        #init cookie jar
        self.cj=cookielib.CookieJar()
        self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders=[("User-Agent","Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3")]
        
    def req(self,url,body=None):
        '''
        Get a request return response body
        '''
        if body is None:
            req=self.opener.open(url)
        elif isinstance(body,tuple):
            req=self.opener.open(url,urllib.urlencode(body))
        else:
            req=self.opener.open(url,body)
        return req.read()
    
    def login(self):
        """
        login in v2ex,return True or False
        """
        url = "http://xfoxtest.appspot.com/a/signin/"
        postdata = (
            ('email',self.username),
            ('pwd',self.pwd),
            )
        
        #login in 
        ret = self.req(url,postdata)
        return ret.find("signout")>-1
        
    def post(self,url,i):
        """
        post test data to /aa/
        """
        postdata = (
            ('title',i),
            ('content','ssss'),
            )
        ret = self.req(url,postdata)
        
if __name__ == "__main__":
    poster = Poster('your email','your pwd')
    print poster.login()
  
    def post(i):
        poster.post('http://xfoxtest.appspot.com/p/aa/',i)
        print i
        
    pool = ThreadPool(10)
    requests = makeRequests(post,range(1,11000))
    for req in requests:
        pool.putRequest(req)
    pool.wait()
        