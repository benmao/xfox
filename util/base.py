#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import random
import time
import string
import md5
import re


def add(x,y):
    return x+y

def random_str(length=6):
    strs = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.sample(strs,length))

def random_md5(str):
    m = md5.new()
    m.update(str)
    m.update(random_str())
    return m.hexdigest()

def encrypt_pwd(pwd,secret_key = None):
    if secret_key is None: 
        secret_key = random_str(6)
    m = md5.new()
    m.update(pwd)
    m.update(secret_key)
    return (secret_key,m.hexdigest())

def check_email(email):
    email = email.lower()
    return len(email)<32 and re.match(r'(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)',email) != None

def check_name(name):
    name = name.lower()
    strset = set("abcdefghijklmnopqrstuvwxyz0123456789")
    return 2<len(name)<17 and set(name) <= strset

def check_pwd(pwd):
    return 5<len(pwd)<17

def get_gmt(date):
    return date.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

if __name__=='__main__':
    pass