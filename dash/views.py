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

from discussion.models import *

class AdminIndexHandler(AdminHandler):
    def get(self):
        self.render("test.html")

class CategoryIndexHandler(AdminHandler):
    def get(self):
        self.template_value['cats']=Category.get_all()
        self.render("category.html")
        
class CategoryDraftedHandler(AdminHandler):
    def get(self):
        self.template_value['cats']=Category.get_draft()
        self.render("category_drafted.html")
        
class CategoryNewHandler(AdminHandler):
    def get(self):
        slug = self.request.get("slug",None)
        if not slug is None:
            self.template_value['category']=Category.get_category(slug)
        self.render("category_new.html")
    
    def post(self):
        title = self.request.get("title").strip()
        slug = self.request.get("slug").strip()
        key_words = self.request.get("key_words")
        description = self.request.get("description")
        
        Category.new(slug,title,key_words,description)
        self.redirect("/d/category/")
    
class CategoryOpertionHandler(AdminHandler):
    def get(self):
        action = self.request.get("action","").strip()
        slug = self.request.get("slug","").strip()

        if action =="draft":
            Category.draft(slug)
        elif action=="undraft":
            Category.un_draft(slug)
        self.redirect("/d/category/")
        
        
def main():
    application = webapp.WSGIApplication([
                                                 ('/d/', AdminIndexHandler),
                                                 ('/d/category/',CategoryIndexHandler),
                                                 ('/d/category/new/',CategoryNewHandler),
                                                 ('/d/category/o/',CategoryOpertionHandler),
                                                 ('/d/category/drafted/',CategoryDraftedHandler),
                                                 ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
