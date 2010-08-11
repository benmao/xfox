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

def check_roles(role_a,role_b):
    return len(set(role_a) & set(role_b))>0

if __name__=='__main__':
    print get_roles()