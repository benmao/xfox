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
        
    def test_check_email(self):
        self.assertTrue(check_email("a@yyer.org"))
        self.assertFalse(check_email("a_sdfsdf.dsfs@sdfdsf.dsfdsfds.fdsfdsf.com"))
        self.assertFalse(check_email("sdfsfd@.cn"))
        self.assertFalse(check_email("@aaa.cn"))
        self.assertFalse(check_email(""))
        self.assertFalse(check_email("a@g.cn<xss>"))
        
    def test_check_name(self):
        self.assertFalse(check_name(""))
        self.assertFalse(check_name("sfd_"))
        self.assertFalse(check_name("11111111111111111111"))
        self.assertTrue(check_name("abDe"))
        
    def test_base36(self):
        base36 = Base36('z')
        self.assertEqual(base36.base10(),35)
        self.assertEqual(base36.base36(35),'z')
        self.assertEqual(base36 + 1,'10')
        self.assertEqual(base36 + '1','10')
        self.assertEqual(base36 + '2','11')
        base36 = base36 + 3
        self.assertEqual(base36,'12')
        

if __name__=='__main__':
    pass