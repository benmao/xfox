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
        
       
class TagIndexHandler(AdminHandler):
    def get(self):
        self.template_value['tags'] = Tag.get_all()
        self.render('tag.html')

class TagNewHandler(AdminHandler):
    def get(self):
        self.template_value['cats']=Category.get_all()
        slug = self.request.get("slug",None)
        if not slug is None:
            self.template_value['tag']=Tag.get_tag_by_slug(slug)
        self.render("tag_new.html")
        
    def post(self):
        title = self.request.get("title").strip()
        slug = self.request.get("slug").strip()
        key_words = self.request.get("key_words")
        description = self.request.get("description")
        category = self.request.get("category")
        Tag.new(slug,title,key_words,description,category)
        self.redirect("/d/tag/")
        
class TagOpertionHandler(AdminHandler):
    def get(self):
        action = self.request.get("action","").strip()
        slug = self.request.get("slug","").strip()

        if action =="draft":
            Tag.draft(slug)
        elif action=="undraft":
            Tag.un_draft(slug)
        self.redirect("/d/tag/")
        
class TagDraftedHandler(AdminHandler):
    def get(self):
        self.template_value['tags']=Tag.get_draft()
        self.render('tag_undrafted.html')
    

def main():
    application = webapp.WSGIApplication([
                                                 ('/d/', AdminIndexHandler),
                                                 ('/d/category/',CategoryIndexHandler),
                                                 ('/d/category/new/',CategoryNewHandler),
                                                 ('/d/category/o/',CategoryOpertionHandler),
                                                 ('/d/category/drafted/',CategoryDraftedHandler),
                                                 
                                                 #tag
                                                 ('/d/tag/',TagIndexHandler),
                                                 ('/d/tag/new/',TagNewHandler),
                                                 ('/d/tag/o/',TagOpertionHandler),
                                                 ('/d/tag/drafted/',TagDraftedHandler),
                                                 
                                                 ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
