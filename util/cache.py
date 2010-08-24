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
register = webapp.template.create_template_register()

class CacheNode(template.Node):
    def __init__(self,nodelist,expire_time_var,fragment_name,vary_on):
        self.nodelist = nodelist
        self.expire_time_var = expire_time_var
        self.fragment_name = fragment_name
        self.vary_on = vary_on
        
    def render(self,context):
        expire_time = int(self.expire_time_var)
        uname = "pu-lic" #None User name can like this
        if not self.vary_on is None:
            try:
                uname = resolve_variable(self.vary_on,context)
            except:
                pass
        
        cache_key = 'template.cache.%s:%s' % (self.fragment_name,uname)
        logging.info(cache_key)
        value = memcache.get(cache_key)
        if value is None:
            logging.info("get data form render : %s" % cache_key)
            value = self.nodelist.render(context)
            memcache.set(cache_key, value, expire_time)
        return value
    
def do_cache(parser, token):
    """
    This will cache the contents of a template fragment for a given amount
    of time.

    Usage::

        {% load cache %}
        {% cache [expire_time] [fragment_name] %}
            .. some expensive processing ..
        {% endcache %}

    This tag also supports varying by a list of arguments::

        {% load cache %}
        {% cache [expire_time] [fragment_name] [var1] [var2] .. %}
            .. some expensive processing ..
        {% endcache %}

    Each unique set of arguments will result in a unique cache entry.
    """
    nodelist = parser.parse(('endcache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise TemplateSyntaxError(u"'%r' tag requires at least 2 arguments." % tokens[0])
    return CacheNode(nodelist, tokens[1], tokens[2], tokens[3] if len(tokens) ==4 else None)

register.tag('cache', do_cache)


if __name__=='__main__':
    pass