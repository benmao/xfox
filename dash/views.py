#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import settings
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from util.acl import *
from util.handler import AdminHandler
from discussion.models import *
from discussion.cell import cell_dict
from account.models import *

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
        
        Category.add_or_update(slug,title,key_words,description)
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
        
class A():
    pass
class TagNewHandler(AdminHandler):
    def get(self):
        self.template_value['cats']=Category.get_all()
        slug = self.request.get("slug",None)
        tag = None
        if not slug is None:
            tag = Tag.get_tag_by_slug(slug)
        roles_list = [] 
        roles = get_roles()
        for role in roles:
            obj = A()
            obj.key,obj.name = role
            if not tag is None and obj.key in tag.role:
                obj.view=True
            if not tag is None and obj.key in tag.add_role:
                obj.add = True
            roles_list.append(obj)
        self.template_value['tag_type'] = cell_dict.keys()
        self.template_value['roles'] = roles_list
        self.template_value['tag']=tag
        self.render("tag_new.html")
        
    def post(self):
        title = self.request.get("title").strip()
        slug = self.request.get("slug").strip()
        key_words = self.request.get("key_words")
        description = self.request.get("description")
        category = self.request.get("category")
        roles = self.request.get("role[]",allow_multiple=True)
        add_roles = self.request.get("add_role[]",allow_multiple=True)
        tag_type = self.request.get("tag_type")
        is_hot = self.request.get("is_hot")
        
        #default role is Guest
        
        if not roles:
            roles = ['G']
    
        kwargs = {
            'tag_type':tag_type,
            'is_hot': True if is_hot else False
            }
        
        Tag.add_or_update(slug,title,key_words,description,category,roles,add_roles,**kwargs)
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
