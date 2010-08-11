#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from google.appengine.ext import db
from util.decorator import *
from util.base import *
from account.models import User,Mention,UserFollow
import datetime
from dash.models import Counter
from util.textile import Textile
from util.paging import PagedQuery
from google.appengine.api.labs import taskqueue

class Category(db.Model):
    '''
    Father of Tag
    '''
    slug = db.StringProperty()
    title = db.StringProperty()
    key_words = db.StringProperty()
    description = db.StringProperty()
    count_tag = db.IntegerProperty(default =0)
    created = db.DateTimeProperty(auto_now_add=True)
    last_updated = db.DateTimeProperty(auto_now=True)
    is_draft = db.BooleanProperty(default =False)
    
    @classmethod
    def new(cls,slug,title,key_words,description):
        slug = filter_url(slug)
        obj = Category.all().filter("slug =",slug).get()
        if obj is None:
            #add new 
            obj=Category(slug=slug)
        
        #update data
        obj.title = title
        obj.key_words = key_words
        obj.description = description
        obj.put()
        
    @classmethod
    def get_all(cls):
        return Category.all().filter("is_draft =",False)
    
    @classmethod
    def get_draft(cls):
        return Category.all().filter("is_draft =",True)
    
    @classmethod
    def get_category(cls,slug):
        return Category.all().filter("slug =",slug).get()
    
    @classmethod
    def draft(cls,slug):
        cat = Category.get_category(slug)
        if not cat is None:
            cat.is_draft= True 
            cat.put()
            
    @classmethod
    def un_draft(cls,slug):
        cat = Category.get_category(slug)
        if not cat is None:
            cat.is_draft= False
            cat.put()
    
class Tag(db.Model):
    '''
    key().name() is slug 
    '''
    category = db.ReferenceProperty(Category)
    title = db.StringProperty()
    key_words = db.StringProperty()
    description = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_updated = db.DateTimeProperty(auto_now = True)
    count_discussion = db.IntegerProperty(default=0)
    allow_discussion = db.BooleanProperty(default =True)
    allow_comment = db.BooleanProperty(default =True)
    is_draft = db.BooleanProperty(default =False)
    
    @delmem("tags")
    def put(self):
        if not self.is_saved(): #create
            self.category.count_tag +=1
            self.category.put() #add category tag count
        super(Tag,self).put()
        
    def delete(self):
        self.category.count_tag -=1
        self.category.put()
        self.is_draft=True
        self.put() # set is_draft 
        
    @property
    def slug(self):
        return self.key().name()
        
    @property
    def url(self):
        return '/%s/' % self.key().name()
    
    @classmethod
    @mem('tags')
    def get_all(cls):
        return Tag.all().filter("is_draft =",False)
    
    @classmethod
    def get_draft(cls):
        return Tag.all().filter("is_draft =",True)
    
    @classmethod
    def check_slug(cls,slug):
        return Tag.get_by_key_name(slug)
    
    @classmethod
    def get_tag_by_slug(cls,slug):
        return Tag.get_by_key_name(slug)
    
    @classmethod
    def new(cls,slug,title,key_words,description,category):
        '''
        Notice:http://code.google.com/intl/en/appengine/docs/python/datastore/keysandentitygroups.html
        '''
        slug = filter_url(slug)
        tag = Tag.check_slug(slug)
        if  tag is None:
            tag = Tag(key_name = slug)
        tag.title=title
        tag.key_words=key_words
        tag.description=description
        tag.category = Category.get(category)
        tag.put()
        return tag
    
    @classmethod
    def draft(cls,slug):
        tag = Tag.get_tag_by_slug(slug)
        if not tag is None:
            tag.is_draft = True
            tag.put()
            
    @classmethod
    def un_draft(cls,slug):
        tag = Tag.get_tag_by_slug(slug)
        if not tag is None:
            tag.is_draft = False
            tag.put()
            
class Discussion(db.Model):
    tag = db.ReferenceProperty(Tag)
    tag_slug = db.StringProperty()
    tag_title = db.StringProperty()
    slug = db.StringProperty()
    title = db.StringProperty(required = True)
    key_words = db.StringProperty()
    description = db.StringProperty()
    content=db.TextProperty(required = True)
    content_formated = db.TextProperty()
    user = db.ReferenceProperty(User)
    user_name = db.StringProperty()
    
    created = db.DateTimeProperty(auto_now_add=True)
    last_updated = db.DateTimeProperty(auto_now=True) 
    last_comment_by = db.StringProperty()
    last_comment = db.DateTimeProperty(auto_now=True)
   
    count_comment =db.IntegerProperty(default=0)
    count_bookmark=db.IntegerProperty(default=0)
    
    source = db.StringProperty(required=False)
    is_draft = db.BooleanProperty(default =False)
    
    f = db.StringProperty() #format type
    is_closed = db.BooleanProperty(default = False)
    
    def put(self):
        if not self.is_saved():
            self.tag.count_discussion +=1
            self.tag.put()
            taskqueue.add( url ='/t/d/follow/' ,params = {'dis':self.key()}) 
        #hander format
        self.content_formated = Textile(restricted=True,lite=False,noimage=False).textile(\
            self.content, rel='nofollow',html_type='xhtml')
        
        self.tag_slug = self.tag.key().name()
        self.tag_title = self.tag.title
        self.slug = self.key().name()
        self.user_name = self.user.name
        super(Discussion,self).put()

    
    def delete(self):
        self.tag.count_discussion -=1
        self.tag.put()
        super(Discussion,self).delete()
        
    @property
    def url(self):
        return "/%s/%s/" % (self.tag_slug,self.key().name())
    
    @classmethod
    def get_discussion_by_key(cls,tag_slug,key):
        return Discussion.get_by_key_name(key)
       # return Discussion.all().filter('key_name =',key).get()
    
    @classmethod
    def is_exist(cls,key):
        return not Discussion.get_by_key_name(key) is None
    
    @classmethod
    def new(self,tag,title,content,user,f='T'):
        key_name = Counter.get_max('discussion').value
        while Discussion.is_exist(key_name):
            key_name = Counter.get_max('discussion').value
        dis = Discussion(key_name = key_name,title=title,content=content,tag=tag)
        dis.f = f
        dis.user = user
        dis.put()
        return dis
    
    @classmethod
    def get_by_tag(cls,tag):
        diss = Discussion.all().filter('tag =',tag).order('-last_comment')
        return PagedQuery(diss,20)
    
    @classmethod
    def get_recent_dis(cls,user):
        return Discussion.all().filter('user =',user).order('-created').fetch(10)
    
    @classmethod
    def get_feed(cls):
        return Discussion.all().order('-created').fetch(10)
    
    @classmethod
    def get_feed_by_tag(cls,tag):
        return Discussion.all().filter('tag =',tag).order('-created').fetch(10)
            
class Bookmark(db.Model):
    user = db.ReferenceProperty(User)
    dis = db.ReferenceProperty(Discussion)
    created = db.DateTimeProperty(auto_now = True)
    is_bookmarked = db.BooleanProperty(default = True)
    
    #
    user_name = db.StringProperty()
    dis_title = db.StringProperty()
    dis_url = db.StringProperty()
    
    def put(self):
        if not self.is_saved():
            self.user.count_bookmarks +=1
            self.user.put()
            self.dis.count_bookmark +=1
            self.dis.put()
        
            self.user_name = self.user.name
            self.dis_title = self.dis.title
            self.dis_url = self.dis.url
        super(Bookmark,self).put()
        
        
    @classmethod
    def get_by_user(cls,user):
        return Bookmark.all().filter('user =',user).order('-created')
    
    @classmethod
    def get_bookmark_users(cls,dis):
        '''
        return bookmark_users
        '''
        users = []
        [usres.append(bookmark.user_name) for bookmark in Bookmark.all().filter('dis =',dis)]
        return users
    
    @classmethod
    def check_bookmarked(cls,user,dis):
        return Bookmark.all().filter('user =',user).filter('dis =',dis).get()
    
    @classmethod
    def get_bookmark(cls,user,dis):
        return Bookmark.all().filter('user =',user).filter('dis =',dis).filter('is_bookmarked =',True).get()
    
    @classmethod
    def do_bookmark(cls,user,dis):
        bookmark = Bookmark.check_bookmarked(user,dis)
        if bookmark is None:
            b = Bookmark(user =user,dis = dis)
            b.put()
            return (True,b)
        elif bookmark.is_bookmarked:
            return (False,None)
        bookmark.is_bookmarked = True
        bookmark.put()
        return (True,bookmark)
    
    @classmethod
    def un_bookmark(cls,user,dis):
        bookmark = Bookmark.check_bookmarked(user,dis)
        if not bookmark is None:
            bookmark.is_bookmarked = False
            bookmark.put()
            
    @classmethod
    def get_recent_bookmark(cls,user):
        tmp = Bookmark.all().filter("user =",user).filter("is_bookmarked =",True).fetch(10)
        return [t.dis for t in tmp]
      
class Comment(db.Model):
    user = db.ReferenceProperty(User)
    dis = db.ReferenceProperty(Discussion)
    slug = db.StringProperty()
    source = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True,indexed = True)
    last_updated = db.DateTimeProperty(auto_now = True)
    
    content = db.TextProperty()
    content_formated = db.TextProperty()
    f = db.StringProperty()
    
    user_name = db.StringProperty()
    dis_slug = db.StringProperty()
    dis_title = db.StringProperty()
    
    is_draft = db.BooleanProperty(default = False)
    is_for_author = db.BooleanProperty(default = False)
    
    @property
    def url(self):
        return "%s#r-%s" % (self.dis_slug,self.slug)

    def put(self):
        if not self.is_saved():
            self.user.count_comments +=1
            self.user.put()
            
            self.dis.count_comment +=1
            self.dis.last_comment_by = self.user.name
            self.dis.put()
            self.user_name = self.user.name
            self.dis_slug = self.dis.url
            self.slug = self.key().name()
        self.content_formated = Textile(restricted=True,lite=False,noimage=False).textile(\
            self.content, rel='nofollow',html_type='xhtml')
        params = {'source_url':self.dis_slug,'source_user':self.user_name}
        self.content_formated=replace_mention(self.content_formated,params)
        RecentCommentLog.new(self.user,self.dis)
        super(Comment,self).put()
        
    @classmethod
    def new(cls,user,dis,content,f='T'):
        key_name = Counter.get_max('comment').value
        while Comment.get_by_key_name(key_name):
            key_name = Counter.get_max('comment').value
        
        comment = Comment(key_name =key_name,user=user,dis = dis ,content=content,f=f)
        comment.put()
        return comment
    
    @classmethod
    def get_by_dis(cls,dis,page=1):
        return Comment.all().filter('dis =',dis)
        
class RecentCommentLog(db.Model):
    user = db.ReferenceProperty(User)
    dis = db.ReferenceProperty(Discussion)
    last_comment = db.DateTimeProperty(auto_now = True)
    
    @classmethod
    def new(cls,user,dis):
        rcl = RecentCommentLog.all().filter('user =',user).filter('dis =',dis).get()
        if rcl is None:
            rcl = RecentCommentLog(user = user,dis = dis)
        rcl.put()
        
    @classmethod
    def get_recent_comment(cls,user):
        tmp = RecentCommentLog.all().filter('user =',user).order('-last_comment').fetch(10)
        return [t.dis for t in tmp]
    
class DiscussionFollow(db.Model):
    dis = db.ReferenceProperty(Discussion)
    user= db.ReferenceProperty(User)
    created = db.DateTimeProperty(auto_now_add = True)
    is_read = db.BooleanProperty(default = False)
    
    @classmethod
    def new(cls,dis):
        obj = Discussion.get(dis)
        followers = UserFollow.get_follower(obj.user)
        for follower in followers:
            disf = DiscussionFollow(dis=obj,user = follower)
            disf.put()
    
    @classmethod
    def get_dis_by_user(cls,user):
        return [df.dis for df in DiscussionFollow.all().filter("user =",user).filter("is_read =",False).order('-created').fetch(100)]
    
if __name__=='__main__':
    pass