#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from util.handler import PublicHandler,PublicWithSidebarHandler
from discussion.models import Tag,Discussion,Comment,Bookmark
import settings
from util.decorator import requires_login,json_requires_login
from util.paging import PagedQuery
from google.appengine.api.labs import taskqueue
from dash.counter import ShardCount
from util.acl import check_roles,check_roles_feed
from util.wsgi  import webapp_add_wsgi_middleware
from google.appengine.api import memcache
import datetime

class TagHandler(PublicWithSidebarHandler):
    def get(self,slug):
        p = int(self.request.get("p","1"))
        tag = Tag.get_tag_by_slug(slug)
        if tag is None:
            return self.error(404)
        
        #check ACL
        check_roles(self,tag.role)
        
        self.template_value['tag']=tag
       
        diss = Discussion.get_by_tag(tag)
        #paging
        prev = p -1 if p >1 else None
        tnext = p+1 if diss.has_page(p+1) else None
       
        self.template_value['prev'] = prev
        self.template_value['next'] = tnext
        self.template_value['diss'] = diss.fetch_page(p)
        self.render('tag.html')

class DiscussionHandler(PublicWithSidebarHandler):
    def get(self,slug,key):
        dis = Discussion.get_discussion_by_key(slug,key)
        if dis is None:
            return self.error(404)
        
        #check ACL
        check_roles(self,dis.role)
        
        #handler visit log
        if not self.user is None:
            key = "%s%s" %(self.user.name_lower,self.p)
            logs = memcache.get(":visitlogs:")
            if logs is None:
                logs = set([])
            logs.add(key)
            memcache.set(":visitlogs:",logs,3600)
        
        self.template_value['disviews']=ShardCount.get_increment_count("disviews:"+key,"disviews")
        self.template_value['dis']=dis
        bookmark = Bookmark.get_bookmark(self.user,dis) if self.user else None
        self.template_value['bookmark'] = bookmark
        comments = Comment.get_by_dis(dis).fetch_page(1)
        self.template_value['comments'] = comments
        self.render("dis.html")
        
class PostDisscussionHandler(PublicHandler):

    @requires_login
    def get(self,slug):
        tag = Tag.get_tag_by_slug(slug)
        if tag is None:
            return self.error(404)
        
        #check ACL
        check_roles(self,tag.role)
        
        self.template_value['tag']=tag
        self.render('p.html')
        
    @requires_login
    def post(self,slug):
        tag = Tag.get_tag_by_slug(slug)
        if tag is None:
            return self.error(404)
        
        #check ACL
        check_roles(self,tag.role)
    
        
        title = self.request.get("title").strip()
        content = self.request.get("content")
        if len(title)>0 and len(content)>0:
            dis =Discussion.new(tag,title,content,self.user,f='M')
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
        
        #check ACL
        check_roles(self,dis.role)
        
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
            dis.f = 'M'
            dis.put()
            self.redirect(dis.url)
        self.template_value['error']=u"不要忘记标题或内容哦"
        #save alter date to dis
        self.template_value['dis']=dis
        self.render('p_edit.html')
        
class PostCommentHandler(PublicWithSidebarHandler):
    def get(self):
        self.error(403)
     
    @requires_login
    def post(self):
        key = self.request.get("key")
        content = self.request.get("content")
        dis = Discussion.get_by_key_name(key)
        if dis is None:
            return self.error(404)
        comment =Comment.new(self.user,dis,content)
        self.redirect(comment.url)
        
class BookmarkHandler(PublicHandler):
    @requires_login
    def get(self):
        
        action = self.request.get("action")
        key = self.request.get("key")
        dis = Discussion.get_by_key_name(key)
        if dis is None:
            return self.error(404)
        if not action in ['un','do']:
            return self.error(404)
        if action =='un':
            Bookmark.un_bookmark(self.user,dis)
        else:
            Bookmark.do_bookmark(self.user,dis)
        self.redirect(dis.url)
        
    @json_requires_login
    def post(self):
        action = self.request.get("action")
        key = self.request.get("key")
        dis = Discussion.get_by_key_name(key)
        funcs = {'un':Bookmark.un_bookmark,
                     'do':Bookmark.do_bookmark,
                     }
        result = {'un':'bookmark',
                      'do':'bookmarked'
                      }
        if not dis is None and action in ['un','do']:
            funcs.get(action)(self.user,dis)
            return self.json({'result':result[action]})
        return self.json({'error':"No handler"})
        
class FeedIndexHandler(PublicHandler):
    def get(self):
        diss = Discussion.get_feed()
        self.template_value['diss']=diss
        self.template_value['lastupdated']=diss[0].created
        self.render('rss.xml')
        
        
class FeedTagHandler(PublicHandler):
    def get(self,key):
        tag = Tag.get_by_key_name(key)
        if tag is None:
            return self.error(404)
        
        #check feed ACL
        if not check_roles_feed(self,tag.role):
            return self.error(403)
    
        diss = Discussion.get_feed_by_tag(tag)
        self.template_value['diss']=diss
        self.template_value['lastupdated']= diss[0].created if len(diss)>0 else datetime.datetime.now()
        self.render('rss.xml')
        
                
class NotFoundHandler(PublicHandler):
    def get(self):
        self.error(404)
        
    def post(self):
        self.error(404)
        
def main():
    application = webapp.WSGIApplication([
                                                          ('/c/?',PostCommentHandler),
                                                          ('/p/(?P<slug>[a-z0-9-]{2,})/?',PostDisscussionHandler),
                                                          ('/p/(?P<slug>[a-z0-9-]{2,})/(?P<key>[a-z0-9]+)/?',EditDisscussionHandler),
                                                          ('/b/?',BookmarkHandler),
                                                          ('/f/?',FeedIndexHandler),
                                                          ('/f/(?P<key>[a-z0-9-]{2,})/?',FeedTagHandler),
                                                          ('/(?P<slug>[a-z0-9-]{2,})/?', TagHandler),
                                                          ('/(?P<slug>[a-z0-9-]{2,})/(?P<key>[a-z0-9]+)/?',DiscussionHandler),
                                                          ('/.*',NotFoundHandler),
                                                          ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(webapp_add_wsgi_middleware(application))

if __name__ == '__main__':
    main()
