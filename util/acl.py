#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/11 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
ROLE= {
    'B':['Banned','Banned User',0],
    'M':['Member','Member User',2],
    'A':['Administrator','Administrator',3],
    'G':['Guest','Guest',1],
}

def get_roles():
    return [(key,ROLE[key][0]) for key in ROLE]

from util.handler import Forbidden
def check_roles(handler,role):
    if len(set(handler.role) & set(role)) > 0:
        return # have perm
    if not handler.user is None:
        raise Forbidden()
    handler.redirect("/a/signin/?go=%s" % handler.request.url)
    
def check_roles_feed(handler,role):
    return 'G' in role

if __name__=='__main__':
    print get_roles()