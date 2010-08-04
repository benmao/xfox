#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import unittest
from util.base import *

class TestBase(unittest.TestCase):
    
    def test_add(self):
        self.assertEqual(add(1,30),31)
    
    def test_random_str(self):
        self.assertEqual(len(random_str(7)),7)
    
    def test_random_md5(self):
        self.assertEqual(len(random_md5("a@sa3.org")),32)

if __name__=='__main__':
    pass