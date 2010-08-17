#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/16 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import settings

class OpenIDLoginHandler(webapp.RequestHandler):
    def get(self):
        go = self.request.get("go","/")
        user = users.get_current_user()
        if user:
            return self.redirect(go)
        else:
            for p_name,p_url in settings.OPENID:
                self.response.out.write('[<a href="%s">%s</a>]' % \
                                        (users.create_login_url(go,None,p_url),p_name))
                    
application = webapp.WSGIApplication([('/_ah/login_required', OpenIDLoginHandler)], debug=settings.DEBUG)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
