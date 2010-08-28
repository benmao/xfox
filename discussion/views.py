#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import settings
import datetime
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api.labs import taskqueue
from google.appengine.api import memcache

from util.base import escape,filter_url
from util.paging import PagedQuery
from util.acl import check_roles,check_roles_feed
from util.wsgi  import webapp_add_wsgi_middleware
from util.decorator import requires_login,json_requires_login
from util.handler import PublicHandler,PublicWithSidebarHandler,FeedHandler,NotFound,get_or_404

from account.models import User
from dash.counter import ShardCount
from discussion.models import Tag,Discussion,Comment,Bookmark
from discussion.cell import get_cell

class TagHandler(PublicWithSidebarHandler):
    def get(self,slug):
        p = int(self.request.get("p","1"))
        tag = get_or_404(Tag.get_tag_by_slug,slug)
        #check ACL
        check_roles(self,tag.role)
        self.p = p
        get_cell(tag.tag_type).tag_list(self,tag)
        
class DiscussionHandler(PublicWithSidebarHandler):
    def get(self,slug,key,p="1"):
        dis = get_or_404(Discussion.get_discussion_by_key,slug,key)
        p = int(p)
        
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
        
        self.template_value['f_tag']={'key':dis.tag_slug,'title':dis.tag_title,'show':'G' in dis.role,'post':True}
        self.template_value['disviews']=ShardCount.get_increment_count("disviews:"+key,"disviews")
        self.template_value['dis']=dis
        bookmark = Bookmark.get_bookmark(self.user,dis) if self.user else None
        self.template_value['bookmark'] = bookmark
        
        #comment page
        comments = PagedQuery(Comment.get_by_dis(dis),self.setting.comment_pagesize)
        temp = comments.fetch_page(p)
        self.template_value['prev']= p-1 if p>1 else None
        self.template_value['next']= p+1 if  len(temp) == self.setting.comment_pagesize else None
        self.template_value['comments'] = temp
        self.template_value['p']=p
        self.render("dis.html")
        
class PostDisscussionHandler(PublicHandler):

    @requires_login
    def get(self,slug):
        tag = get_or_404(Tag.get_tag_by_slug,slug)
        #check ACL
        check_roles(self,tag.role)
        check_roles(self,tag.add_role) #addrole
        
        self.m = 'get'
        get_cell(tag.tag_type).add(self,tag)
        
    @requires_login
    def post(self,slug):
        tag = get_or_404(Tag.get_tag_by_slug,slug)
        #check ACL
        check_roles(self,tag.role)
        check_roles(self,tag.add_role)
        
        self.m = 'post'
        get_cell(tag.tag_type).add(self,tag)
            
class EditDisscussionHandler(PublicHandler):
    @requires_login
    def get(self,slug,key):
        dis = get_or_404(Discussion.get_discussion_by_key,slug,key)
        #check ACL
        check_roles(self,dis.role)
        
        if dis.user_name != self.user.name :
            return self.error(403) #shoud be 403 :)
        
        self.m = 'get'
        get_cell(dis.tag.tag_type).edit(self,dis)
        
    @requires_login
    def post(self,slug,key):
        dis = get_or_404(Discussion.get_discussion_by_key,slug,key)
         #check ACL
        check_roles(self,dis.role)
        
        if dis.user_name != self.user.name :
            return self.error(403) #shoud be 403 :)
        
        self.m = 'post'
        get_cell(dis.tag.tag_type).edit(self,dis)
        
class PostCommentHandler(PublicWithSidebarHandler):
    def get(self):
        self.error(403)
     
    @requires_login
    def post(self):
        key = self.request.get("key")
        content = self.request.get("content")
        dis = get_or_404(Discussion.get_by_key_name,key)
        comment =Comment.new(self.user,dis,content)
        self.redirect(comment.url)
        
class PostCommentAjaxHandler(PublicHandler):
    def get(self):
        self.error(403)
        
    @requires_login
    def post(self):
        key = self.request.get("key")
        logging.info(key)
        content = self.request.get("content")
        ip = self.request.remote_addr
        user_agent =  escape(self.request.headers.get('User-Agent','Firefox'))
        if not content.strip():
            return self.json({'error':u"内容不能为空"})
        dis = Discussion.get_by_key_name(key)
        if dis is None:
            return self.json({'error':u"不要非法提交哦"})
        if dis.is_closed:
            return self.json({'error':u"评论已经关闭"})
        comment = Comment.new(self.user,dis,content,ip=ip,user_agent=user_agent)
        self.template_value['comment']=comment
        return self.json({'success':True,'comment':self.get_render("comment.html")})
    
    
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
        
class FeedIndexHandler(FeedHandler):
    def get(self):
        diss = Discussion.get_feed()
        self.template_value['diss']=diss
        self.template_value['lastupdated']=diss[0].created
        self.render('rss.xml')
        
        
class FeedTagHandler(FeedHandler):
    def get(self,key):
        tag = get_or_404(Tag.get_by_key_name,key)
        
        #check feed ACL
        if not check_roles_feed(self,tag.role):
            return self.error(403)
    
        diss = Discussion.get_feed_by_tag(tag)
        self.template_value['diss']=diss
        self.template_value['lastupdated']= diss[0].created if len(diss)>0 else datetime.datetime.now()
        self.render('rss.xml')
        
class FeedUserHandler(FeedHandler):
    def get(self,name):
        user = get_or_404(User.get_user_by_name,name)
        diss = Discussion.get_recent_dis(user)
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
                                                          #('/c/?',PostCommentHandler),
                                                          ('/c/ajax/',PostCommentAjaxHandler),
                                                          ('/p/(?P<slug>[a-z0-9-]{2,})/?',PostDisscussionHandler),
                                                          ('/p/(?P<slug>[a-z0-9-]{2,})/(?P<key>[a-z0-9-]+)/?',EditDisscussionHandler),
                                                          ('/b/?',BookmarkHandler),
                                                          ('/f/?',FeedIndexHandler),
                                                          ('/f/(?P<key>[a-z0-9-]{2,})/?',FeedTagHandler),
                                                          ('/f/u/(?P<name>[a-z0-9]{3,16})/?',FeedUserHandler),
                                                          ('/(?P<slug>[a-z0-9-]{2,})/?', TagHandler),
                                                          ('/(?P<slug>[a-z0-9-]{2,})/(?P<key>[a-z0-9-]+)/?',DiscussionHandler),
                                                          ('/(?P<slug>[a-z0-9-]{2,})/(?P<key>[a-z0-9-]+)/(?P<p>[0-9]+)/?',DiscussionHandler),
                                                          ('/.*',NotFoundHandler),
                                                          ],
                                         debug=settings.DEBUG)
    util.run_wsgi_app(webapp_add_wsgi_middleware(application))

if __name__ == '__main__':
    main()
