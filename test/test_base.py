#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import unittest
from util.base import add

class TestBase(unittest.TestCase):
    
    def test_add(self):
        self.assertEqual(add(1,30),31)
    

if __name__=='__main__':
    pass