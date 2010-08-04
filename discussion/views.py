#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from account.models import A

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')


def main():
    application = webapp.WSGIApplication([('/b/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
