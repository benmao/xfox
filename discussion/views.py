#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from util.handler import PublicHandler,PublicWithSidebarHandler
from discussion.models import Tag,Discussion
import settings
from util.decorator import requires_login

class TagHandler(PublicWithSidebarHandler):
    def get(self,slug):
        tag = Tag.get_tag_by_slug(slug)
        if tag is None:
            return self.error(404)
        self.template_value['tag']=tag
        self.template_value['diss']=Discussion.get_by_tag(tag)
        self.render('tag.html')

class DiscussionHandler(PublicWithSidebarHandler):
    def get(self,slug,key):
        dis = Discussion.get_discussion_by_key(slug,key)
        if dis is None:
            return self.error(404)
        self.template_value['dis']=dis
        self.render("dis.html")
        
class PostDisscussionHandler(PublicHandler):

    @requires_login
    def get(self,slug):
        tag = Tag.get_tag_by_slug(slug)
        if tag is None:
            return self.error(404)
        self.template_value['tag']=tag
        self.render('p.html')
        
    @requires_login
    def post(self,slug):
        tag = Tag.get_tag_by_slug(slug)
        if tag is None:
            return self.error(404)
        title = self.request.get("title").strip()
        content = self.request.get("content")
        if len(title)>0 and len(content)>0:
            dis =Discussion.new(tag,title,content,self.user)
            self.redirect(dis.url)
        self.template_value['error']=u"不要忘记标题或内容哦"
        self.template_value['title']=title
        self.template_value['content']=content
        self.render('p.html')
            
class EditDisscussionHandler(PublicHandler):
    @requires_login
    def get(self,slug,key):
        dis = Discussion.get_discussion_by_key(slug,key)
        if dis is None:
            return self.error(404)
        if dis.user_name != self.user.name :
            return self.error(403) #shoud be 403 :)
        self.template_value['dis']=dis
        self.render("p_edit.html")
        
    @requires_login
    def post(self,slug,key):
        title = self.request.get("title").strip()
        content = self.request.get("content").strip()
        dis = Discussion.get_discussion_by_key(slug,key)
        if len(title)> 0 and len(content) > 0:
            if  dis is None:
                return self.error(404)
            if dis.user_name != self.user.name:
                return self.error(403)
            dis.title = title
            dis.content = content
            dis.put()
            self.redirect(dis.url)
        self.template_value['error']=u"不要忘记标题或内容哦"
        #save alter date to dis
        self.template_value['dis']=dis
        self.render('p_edit.html')
        
        
class NotFoundHandler(PublicHandler):
    def get(self):
        self.error(404)
        
    def post(self):
        self.error(404)
        
def main():
    application = webapp.WSGIApplication([
                                                          ('/p/(?P<slug>[a-z0-9-]{2,})/',PostDisscussionHandler),
                                                          ('/p/(?P<slug>[a-z0-9-]{2,})/(?P<key>[a-z0-9]+)/',EditDisscussionHandler),
                                                          ('/(?P<slug>[a-z0-9-]{2,})/', TagHandler),
                                                          ('/(?P<slug>[a-z0-9-]{2,})/(?P<key>[a-z0-9]+)/',DiscussionHandler),
                                                          
                                                          ('/.*',NotFoundHandler),
                                                          ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
