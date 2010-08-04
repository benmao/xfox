#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import unittest
import logging

from account.models import Invitation

class TestInvitation(unittest.TestCase):
    
    def test_check_invition(self):
        self.assertEqual(Invitation.check_invitation("sssssss@sa3.org"),None)

if __name__=='__main__':
    pass