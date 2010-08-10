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
from google.appengine.api.labs import taskqueue
import logging

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

class Base36():
    def __init__(self,num):
        self.s ="0123456789abcdefghijklmnopqrstuvwxyz"
        if not set(num) <= set(self.s):
            raise ValueError('number must be in "[0-9a-z]"')
        self.num = num
    
    def base10(self):
        '''
        return base 10 number
        '''
        return int(self.num,36)
    
    def __len__(self):
        return len(self.num)
    
    def base36(self,num):
        if not isinstance(num,(int,long)):
            raise TypeError('num must be an integer')
        if num < 0:
            raise ValueError('num must be positive')
        if num < 36:
            return self.s[num]
        b=''
        while num !=0:
            num,i = divmod(num,36)
            b = self.s[i]+b
        return b
    
    def __add__(self,num):
        if isinstance(num,(int,long)):
            return self.base36(int(self.num,36)+num)
        return self.base36(int(self.num,36)+int(num,36))
    
def filter_url(url):
    '''
    url contains [a-z0-9-]
    can not startswith or endswith '-'
    '''
    url = url.strip().lower()
    url = re.sub(r'\W+',' ',url)
    url = url.strip()
    return url.replace(' ','-')

def re_mention(value):
    return re.findall(r'@([a-zA-Z0-9]{3,16}\.?)',value)

def joinstr(*values):
    return ''.join(values)

def replace_mention(value,params):
    mentions = re_mention(value)
    if len(mentions)>0:
        mentions = set(mentions)
        num = 0
        for mention in mentions:
            if num >5:
                break  #limit 5 mentions
            if mention.endswith('.'):
                continue #should be email
            value = value.replace(joinstr("@",mention),'@<a href="/u/%s/" >%s</a>' % (mention,mention))
            params['user']=mention
            taskqueue.add(url ="/t/u/mention/",params=params)
            num +=1
    return value
if __name__=='__main__':
    print replace_mention("@benben")