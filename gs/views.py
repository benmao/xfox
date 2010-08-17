#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/9 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import settings
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from util.handler import PublicHandler,PublicWithSidebarHandler
from util.decorator import requires_login
from gs.models import GSFile,LatexImage
from util.wsgi import webapp_add_wsgi_middleware

class GsFileIndexHandler(PublicWithSidebarHandler):
    @requires_login
    def get(self):
        self.template_value['gss']=GSFile.get_gsfile_by_user(self.user)
        self.render("g.html")
    
class GsUploadHandler(PublicWithSidebarHandler):
    @requires_login
    def get(self):
        self.render("g_upload.html")
        
    @requires_login    
    def post(self):
        bf = self.request.get("file")
        if not bf:
            return self.redirect("/g/upload/")
        name = unicode(self.request.body_file.vars['file'].filename,'utf-8')
        mime = self.request.body_file.vars['file'].headers['content-type']
        
        if mime.find("image")<0:
            return self.redirect("/g/upload/")
        if len(bf) > 1024*1000:
            return self.redirect("/g/upload/")
       
        GSFile.new(name,mime,bf,self.user)
        self.redirect("/g/")
        
class LatexImageHandler(PublicHandler):
    def get(self,key):
        latex = LatexImage.get_by_key_name(key)
        if latex is None:
            return self.error(404)
        if latex.is_done:
            return self.redirect(latex.url,True)
        return self.error(404)
        
def main():
    application = webapp.WSGIApplication([
                                        ('/g/', GsFileIndexHandler),
                                        ('/g/upload/',GsUploadHandler),
                                        ('/g/latex/(?P<key>[a-z0-9]{32})/',LatexImageHandler),
                                        ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(webapp_add_wsgi_middleware(application))

if __name__=='__main__':
    main()