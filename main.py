#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from util.handler import PublicHandler
from util.decorator import requires_login
class MainHandler(PublicHandler):

    #@requires_login
    def get(self):
        self.error(404)
    
    def post(self):
        self.error(404)
        
def main():
    application = webapp.WSGIApplication([('/.*', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
