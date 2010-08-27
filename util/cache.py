#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/23 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import logging
from django import template
from django.template import Context,Template,loader,resolve_variable
from google.appengine.api import memcache
from google.appengine.ext import webapp

from util import cachepy


register = webapp.template.create_template_register()

class CacheNode(template.Node):
    def __init__(self,nodelist,cache,expire_time_var,fragment_name,vary):
        '''
        args:
        nodelist:nodelist object
        cache: cache object in [memcache,filecache]
        expire_time_var: cache expire_time
        '''
        self.nodelist = nodelist
        self.cache = cache
        self.fragment_name = fragment_name
        self.expire_time_var = int(expire_time_var)
        self.vary = vary
        
    def render(self,context):
        user_name = context['user'].name_lower if 'user' in context and context['user'] else 'pu-lic'
        path = context['tp']
        if 'user' in self.vary and 'path' in self.vary:
            cache_key = 'template.cache.%s:%s:%s' % (self.fragment_name,user_name,path)
        elif 'user' in self.vary:
            cache_key = 'template.cache.%s:%s' % (self.fragment_name,user_name)
        elif 'path' in self.vary:
            cache_key = 'template.cache.%s:%s' % (self.fragment_name,path)
        else:
            cache_key = 'template.cache.%s' % (self.fragment_name)
            
        logging.info(cache_key)
        value = self.cache.get(cache_key)
        if value is None:
            logging.info("get data form render : %s" % cache_key)
            value = self.nodelist.render(context)
            self.cache.set(cache_key, value, self.expire_time_var)
        return value
    
def do_memcache(parser,token):
    nodelist = parser.parse(('endmemcache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens)<3:
        raise TemplateSyntaxError(u"'%r' tag requires at least 2 arguments." % tokens[0])
    return CacheNode(nodelist,memcache,tokens[1],tokens[2],tokens[3:])

def do_cache(parser,token):
    nodelist = parser.parse(('endcache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens)<3:
        raise TemplateSyntaxError(u"'%r' tag requires at least 2 arguments." % tokens[0])
    return CacheNode(nodelist,memcache,tokens[1],tokens[2],tokens[3:])

def do_filecache(parser,token):
    nodelist = parser.parse(('endfilecache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens)<3:
        raise TemplateSyntaxError(u"'%r' tag requires at least 2 arguments." % tokens[0])
    return CacheNode(nodelist,cachepy,tokens[1],tokens[2],tokens[3:])


register.tag('memcache',do_memcache)
register.tag('cache',do_cache)
register.tag('filecache',do_filecache)

if __name__=='__main__':
    pass