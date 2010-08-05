#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import settings
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from util.handler import AdminHandler


class AdminIndexHandler(AdminHandler):
    def get(self):
        self.render("test.html")


def main():
    application = webapp.WSGIApplication([
                                                 ('/b/', AdminIndexHandler),
                                                 ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
