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
from util.paging import PagedQuery
import markdown
from google.appengine.api.labs import taskqueue
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
    
    role = db.StringListProperty()
    
    @delmem("tags")
    def put(self):
        if not self.is_saved(): #create
            self.category.count_tag +=1
            self.category.put() #add category tag count
        else:
            memcache.delete("tag:%s" % self.key().name()) #delete memcache
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
    def get_tag_by_slug(cls,slug):
        @mem("tag:%s" % slug)
        def _x(slug):
            return Tag.get_by_key_name(slug)
        return _x(slug)
    
    @classmethod
    def new(cls,slug,title,key_words,description,category,role):
        '''
        Notice:http://code.google.com/intl/en/appengine/docs/python/datastore/keysandentitygroups.html
        '''
        slug = filter_url(slug)
        if len(slug)<2:
            return None
        tag = Tag.get_by_key_name(slug)
        if  tag is None:
            tag = Tag(key_name = slug)
        tag.title=title
        tag.key_words=key_words
        tag.description=description
        tag.category = Category.get(category)
        tag.role = role
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
    
    @delmem("feeddiscussion")
    def put(self):
        if not self.is_saved():
            ShardCount.get_increment_count("tagcount:"+self.tag.key().name(),"tagcount")
            taskqueue.add( url ='/t/d/follow/' ,params = {'dis':self.key()}) 
        else:
            self.last_updated = datetime.datetime.now() #update
            if self.edit_number:
                self.edit_number+=1
            else:
                self.edit_number=1
            memcache.delete("dis:%s:%s"%(self.tag_slug,self.key().name()))
        #hander format
        self.title=escape(self.title) 
        self.content_formated = FORMAT_METHOD.get('M',get_markdown)(self.content)
        self.role = self.tag.role
        self.tag_slug = self.tag.key().name()
        self.tag_title = self.tag.title
        self.slug = self.key().name()
        self.user_name = self.user.name
        super(Discussion,self).put()
    
    def delete(self):
        super(Discussion,self).delete()
        
    def nobody(self):
        ShardCount.decrement("tagcount:"+self.tag.key().name())
        self.is_closed = True
        self.put()
        
    @property
    def url(self):
        return "/%s/%s/" % (self.tag_slug,self.key().name())
    
    @classmethod
    def get_discussion_by_key(cls,tag_slug,key):
        @mem("dis:%s:%s"%(tag_slug,key))
        def _x(tag_slug,key):
            dis = Discussion.get_by_key_name(key)
            return dis if dis and dis.tag_slug == tag_slug else None
        return _x(tag_slug,key)
    
    @classmethod
    def get_recent(cls):
        return Discussion.all().order('-last_comment').fetch(15)
    
        
    @classmethod
    def is_exist(cls,key):
        return not Discussion.get_by_key_name(key) is None
    
    @classmethod
    def new(self,tag,title,content,user,f='T'):
        key_name = Counter.get_max('discussion').value
        while Discussion.is_exist(key_name):
            key_name = Counter.get_max('discussion').value
        dis = Discussion(key_name = key_name,title=title,content=content,tag=tag,f=f,user = user)
        dis.put()
        return dis
    
    @classmethod
    def get_by_tag(cls,tag):
        diss = Discussion.all().filter('tag =',tag).order('-last_comment')
        return PagedQuery(diss,15)
        
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
            ShardCount.get_increment_count("userbookmark:"+self.user.name,"userbookmark")
            ShardCount.get_increment_count("disbookmark:"+self.dis.key().name(),"disbookmark")
            self.user_name = self.user.name
            self.dis_title = self.dis.title
            self.dis_url = self.dis.url
        super(Bookmark,self).put()
        
    def delete(self):
        #ShardCount.decrement("userbookmark:"+self.user_name)
        #ShardCount.decrement("disbookmark:"+self.dis.key().name())
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
    
    @property
    def url(self):
        return "%s#r-%s" % (self.dis_slug,self.slug)

    def put(self):
        if not self.is_saved():
            ShardCount.get_increment_count("usercomments:"+self.user.name,"usercomments")
            #ShardCount.get_increment_count("discomments:"+self.dis.key().name(),"discomments")
            self.dis.count_comment+=1
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
    def new(cls,user,dis,content,f='M'):
        key_name = Counter.get_max('comment').value
        while Comment.get_by_key_name(key_name):
            key_name = Counter.get_max('comment').value
        
        comment = Comment(key_name =key_name,user=user,dis = dis ,content=content,f=f)
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
        followers = UserFollow.get_follower(obj.user)
        for follower in followers:
            disf = DiscussionFollow(dis=obj,user = follower)
            disf.put()
    
    @classmethod
    def get_dis_by_user(cls,user):
        return [df.dis for df in DiscussionFollow.all().filter("user =",user).filter("is_read =",False).order('-created').fetch(100)]
    
if __name__=='__main__':
    pass