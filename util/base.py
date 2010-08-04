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

if __name__=='__main__':
    pass