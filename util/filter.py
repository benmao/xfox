#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/7 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

import datetime
from google.appengine.ext import webapp
register = webapp.template.create_template_register()

def datetz(value,arg):
    t = datetime.timedelta(seconds=3600*8) #8hour
    return webapp.template.django.template.defaultfilters.date(value+t, arg)

register.filter(datetz)

def humdate(value):
    tmp = datetime.datetime.now() -value
    if tmp.days > 0:
        return datetz(value,"m-d H:i")
    if tmp.seconds < 60:
        return u"%s 秒前" % tmp.seconds
    if tmp.seconds <3600:
        return u"约%s分钟前" % (tmp.seconds/60)
    return u"约%s小时前" % (tmp.seconds/3600)

register.filter(humdate)

def humpage(value):
    '''
    if page == 1 return ""
    else return ?p = value
    '''
    if value == 1:
        return ""
    return "?p=%s" % value

register.filter(humpage)

def cut(value,length):
    return value[0:length]

register.filter(cut)

if __name__=='__main__':
    pass