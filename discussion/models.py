#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/4 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import markdown
import datetime

from google.appengine.ext import db
from google.appengine.api.labs import taskqueue

from util.decorator import *
from util.base import *
from util.paging import PagedQuery

from account.models import User,Mention,UserFollow
from dash.models import Counter
from dash.counter import ShardCount


def get_markdown(value):
    return markdown.Markdown(safe_mode="escape").convert(value)

FORMAT_METHOD = {
    'M':get_markdown,
    }

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
    def add_or_update(cls,slug,title,key_words,description):
        slug = filter_url(slug)
        cat = Category.all().filter("slug =",slug).get() or Category(slug=slug)

        kwargs = {
            'title':escape(title),
            'key_words':escape(key_words),
            'description':escape(description),
            }
        
        for k in kwargs:
            setattr(cat,k,kwargs[k])
        
        cat.put()
        
    @property
    def tags(self):
        return Tag.all().filter('category =',self).filter('is_draft =',False).filter('role =','G')
    
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
    
    role = db.StringListProperty()
    add_role = db.StringListProperty()
    
    tag_type = db.StringProperty()
   
    is_hot = db.BooleanProperty(default=True)
    
    @delmem("tags")
    def put(self):
        if self.is_saved(): #update
            memcache.delete("tag:%s" % self.key().name()) #delete memcache
        super(Tag,self).put()
        
    def delete(self):
        self.is_draft=True
        self.put() # set is_draft 
        
    @property
    def slug(self):
        return self.key().name()
        
    @property
    def url(self):
        return '/%s/' % self.key().name()
    
    @classmethod
    def get_all(cls):
        return Tag.all().filter("is_draft =",False)

    @classmethod
    def get_hot(cls,limit=50):
        return Tag.all().filter("is_hot =",True).order("count_discussion").fetch(limit)
    
    @classmethod
    def get_draft(cls):
        return Tag.all().filter("is_draft =",True)
    
    @classmethod
    def get_tag_by_slug(cls,slug):
        @mem("tag:%s" % slug)
        def _x(slug):
            return Tag.get_by_key_name(slug)
        return _x(slug)
    
    @classmethod
    def add_or_update(cls,slug,title,key_words,description,category,role,add_role,**kwargs):
        '''
        Notice:http://code.google.com/intl/en/appengine/docs/python/datastore/keysandentitygroups.html
        '''
        slug = filter_url(slug)
        if len(slug)<2:
            return None
        tag = Tag.get_by_key_name(slug) or Tag(key_name = slug)
        kwargs.update({
            'title' : escape(title),
            'key_words' : escape(key_words),
            'description' : description,
            'category' : Category.get(category),
            'role':role,
            'add_role':add_role,
            })
        for k in kwargs:
            setattr(tag,k,kwargs[k])
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
            
class Discussion(db.Expando):
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
    last_updated = db.DateTimeProperty(auto_now_add = True) #update 
    edit_number = db.IntegerProperty(default=1)
    
    last_comment_by = db.StringProperty()
    last_comment = db.DateTimeProperty(auto_now_add=True)
   
    count_bookmark=db.IntegerProperty(default=0)
    count_comment = db.IntegerProperty(default=0)
    
    source = db.StringProperty(required=False)
    is_draft = db.BooleanProperty(default =False)
    
    f = db.StringProperty() #format type
    is_closed = db.BooleanProperty(default = False)
    
    role = db.StringListProperty()
   
    
    ip = db.StringProperty()
    user_agent = db.StringProperty()

    prev_slug = db.StringProperty() 
    prev_title = db.StringProperty()
    
    next_slug = db.StringProperty()
    next_title = db.StringProperty()
    
    img_url = db.StringProperty() #for Image Album
    
    @delmem("feeddiscussion")
    def put(self):
        if not self.is_saved():
            taskqueue.add( url ='/t/d/follow/' ,params = {'dis':self.key()})
            self.role = self.tag.role
            self.tag_slug = self.tag.key().name()
            self.tag_title = self.tag.title
            self.user_name = self.user.name
        else: #edit
            self.last_updated = datetime.datetime.now() #update
            if self.edit_number:
                self.edit_number+=1
            else:
                self.edit_number=1
            memcache.delete("dis:%s"%(self.key().name()))
        #hander format
        self.content_formated = FORMAT_METHOD.get('M',get_markdown)(self.content)
        super(Discussion,self).put()
    
    def delete(self):
        super(Discussion,self).delete()
        
    @property
    def url(self):
        return "/%s/%s/" % (self.tag_slug,self.slug)
    
    @classmethod
    def get_discussion_by_key(cls,tag_slug,key):
        @mem("dis:%s:%s"%(tag_slug,key))
        def _x(tag_slug,key):
            return  Discussion.get_by_key_name("%s:%s" %(tag_slug,key))
        return _x(tag_slug,key)
    
    @classmethod
    def get_recent(cls):
        return Discussion.all().order('-last_comment').fetch(15)
        
    @classmethod
    def is_exist(cls,key):
        return not Discussion.get_by_key_name(key) is None

    @classmethod
    def check_slug(cls,tag_slug,slug):
        return not Discussion.get_by_key_name("%s:%s" %(tag_slug,slug)) is None
    
    @classmethod
    def add(cls,tag,slug,title,content,user,**kwargs):
        tag_key = tag.key().name()
        slug = filter_url(slug) or Counter.get_max(":%s:" % tag_key).value
        key_name = "%s:%s" % (tag_key,slug)
        while Discussion.is_exist(key_name):
            slug = Counter.get_max(":%s:" % tag.key().name()).value
            key_name = "%s:%s" % (tag_key,slug)
            
        dis = Discussion(key_name = key_name,tag = tag,slug = slug,title=title,content=content,user=user,**kwargs)
        dis.put()
        return dis
     
    
    @classmethod
    def get_by_tag(cls,tag,page_size=15):
        diss = Discussion.all().filter('tag =',tag).order('-last_comment')
        return PagedQuery(diss,page_size)
        
    @classmethod
    def get_recent_dis(cls,user):
        return Discussion.all().filter('user =',user).order('-created').fetch(10)
    
    @classmethod
    @mem("feeddiscussion")
    def get_feed(cls):
        return Discussion.all().filter('role =','G').order('-created').fetch(20)
    
    @classmethod
    def get_feed_by_tag(cls,tag):
        return Discussion.all().filter('tag =',tag).order('-created').fetch(10)
            
class Bookmark(db.Model):
    user = db.ReferenceProperty(User)
    dis = db.ReferenceProperty(Discussion)
    created = db.DateTimeProperty(auto_now = True)
    
    #
    user_name = db.StringProperty()
    dis_title = db.StringProperty()
    dis_url = db.StringProperty()
    
    def put(self):
        if not self.is_saved():
            self.user_name = self.user.name
            self.dis_title = self.dis.title
            self.dis_url = self.dis.url
        super(Bookmark,self).put()
        
    def delete(self):
        super(Bookmark,self).delete()
        
        
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
        return Bookmark.all().filter('user =',user).filter('dis =',dis).get()
    
    @classmethod
    def do_bookmark(cls,user,dis):
        bookmark = Bookmark.check_bookmarked(user,dis)
        if bookmark is None:
            b = Bookmark(user =user,dis = dis)
            b.put()
    
    @classmethod
    def un_bookmark(cls,user,dis):
        bookmark = Bookmark.check_bookmarked(user,dis)
        if not bookmark is None:
            bookmark.delete()
            
    @classmethod
    def get_recent_bookmark(cls,user):
        tmp = Bookmark.all().filter("user =",user).order('created').fetch(10)
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
    
    ip = db.StringProperty()
    user_agent = db.StringProperty()
    
    @property
    def url(self):
        return "%s#r-%s" % (self.dis_slug,self.slug)

    def put(self):
        if not self.is_saved():
            self.dis.last_comment_by = self.user.name
            self.dis.last_comment = datetime.datetime.now()
            self.dis.put()
            self.user_name = self.user.name
            self.dis_slug = self.dis.url
            self.slug = self.key().name()
        self.content_formated= FORMAT_METHOD.get('M',get_markdown)(self.content)
        params = {'source_url':self.dis_slug,'source_user':self.user_name}
        self.content_formated=replace_mention(self.content_formated,params)
        RecentCommentLog.new(self.user,self.dis)
        super(Comment,self).put()
        
    @classmethod
    def new(cls,user,dis,content,f='M',ip='127.0.0.1',user_agent='Firefox'):
        key_name = Counter.get_max('comment').value
        while Comment.get_by_key_name(key_name):
            key_name = Counter.get_max('comment').value
        
        comment = Comment(key_name =key_name,user=user,dis = dis ,content=content,f=f,ip=ip,user_agent=user_agent)
        comment.put()
        return comment
    
    @classmethod
    def get_by_dis(cls,dis):
        return PagedQuery(Comment.all().filter('dis =',dis).order('created'),100)
        
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

class DiscussionVisitLog(db.Model):
    user_name = db.StringProperty()
    tag_key = db.StringProperty()
    dis_key = db.StringProperty()
    created  = db.DateTimeProperty(auto_now_add = True)
    
    @classmethod
    def new(cls,user_name,tag_key,dis_key):
        key_name = "%s:%s:%s" % (user_name,tag_key,dis_key)
        dvl = DiscussionVisitLog.get_by_key_name(key_name)
        if dvl is None:
            dvl = DiscussionVisitLog(key_name = key_name,user_name = user_name,tag_key=tag_key,dis_key=dis_key)
            dvl.put()
    
class DiscussionFollow(db.Model):
    dis = db.ReferenceProperty(Discussion)
    user= db.ReferenceProperty(User)
    created = db.DateTimeProperty(auto_now_add = True)
    is_read = db.BooleanProperty(default = False)
    
    @classmethod
    def new(cls,dis):
        obj = Discussion.get(dis)
        if obj is None:
            return
        followers = UserFollow.get_follower(obj.user)
        for follower in followers:
            disf = DiscussionFollow(dis=obj,user = follower)
            disf.put()
    
    @classmethod
    def get_dis_by_user(cls,user):
        return  DiscussionFollow.all().filter("user =",user).filter("is_read =",False).order("-created").fetch(30)
        #return [df.dis for df in DiscussionFollow.all().filter("user =",user).filter("is_read =",False).order('-created').fetch(100)]
        
    @classmethod
    def set_read(cls,key):
        follow = DiscussionFollow.get(key)
        if not follow is None:
            follow.is_read = True
            follow.put()
            return True
        return False

    @classmethod
    def check_follow(cls,user):
        return DiscussionFollow.all().filter("user =",user).filter("is_read =",False).count()
    
if __name__=='__main__':
    pass