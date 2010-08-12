#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/11 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
ROLE= {
    'B':['Banned','Banned User'],
    'M':['Member','Member User'],
    'A':['Administrator','Administrator'],
    'G':['Guest','Guest'],
}

def get_roles():
    return [(key,ROLE[key][0]) for key in ROLE]

def check_roles(handler,role):
    if len(set(handler.role) & set(role)) > 0:
        return # have perm
    if not handler.user is None:
        return handler.redirect("/a/notallowed/")
    handler.redirect("/a/signin/?go=%s" % handler.request.url)
    
def check_roles_feed(handler,role):
    return 'G' in role

if __name__=='__main__':
    print get_roles()