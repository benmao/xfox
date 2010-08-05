#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/5 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import unittest
import logging

from util.decorator import mem,delmem
from google.appengine.api import memcache

class TestMem(unittest.TestCase):
    
    def test_mem(self):
       
        @mem("a")
        def add(x,y):
            return x+y
        
        @delmem("a")
        def d():
            pass
        
        a = add(1,2)
        self.assertAlmostEqual(a,memcache.get("a"))

if __name__=='__main__':
    pass