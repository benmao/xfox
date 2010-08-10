#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/9 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from google.appengine.ext import db
from account.models import User
import settings
from boto.gs.connection import GSConnection
from dash.models import Counter
from google.appengine.api import images
import logging

class GSFile(db.Model):
    user = db.ReferenceProperty(User)
    user_name = db.StringProperty()
    
    name = db.StringProperty()
    mime = db.StringProperty()
    size = db.IntegerProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    cname = db.StringProperty()
    
    is_disscussion = db.BooleanProperty(default = True)
    width = db.IntegerProperty(default=0)
    heigth = db.IntegerProperty(default=0)
    small_pic = db.StringProperty()
    
    
    def put(self):
        if not self.is_saved():
            self.user_name=self.user.name
            super(GSFile,self).put()
            
    def save_to_gs(self,key_name,bf,png=False):
        conn = GSConnection(gs_access_key_id = settings.gs_access_key_id,gs_secret_access_key =settings.gs_secret_access_key)
        bucket = conn.get_bucket(settings.bucket_name)
        gs_file = bucket.new_key(key_name)
        mime = ' image/png ' if png else  self.mime
        gs_file.set_contents_from_string(bf,policy="public-read",headers={"Content-Type":mime})
        
        
    @property
    def url(self):
        return "%s/%s" % (self.cname,self.key().name())
    
    @property
    def surl(self):
        return "%s/%s" % (self.cname,self.small_pic)
    
    @classmethod
    def new(cls,name,mime,bf,user):
        key_name = Counter.get_max("gs").value
        img = images.Image(bf)
        
        gsfile = GSFile(key_name=key_name,name =name,mime=mime,size =len(bf),user=user,cname = settings.cname)
        gsfile.width = img.width
        gsfile.heigth= img.height
        gsfile.small_pic=key_name

        if img.height > 450: #need resize
            img.resize(width=500)
            img.im_feeling_lucky()
            gsfile.save_to_gs('s/'+key_name,img.execute_transforms(output_encoding=images.PNG),True)
            gsfile.small_pic='s/'+key_name
        gsfile.save_to_gs(key_name,bf)
        gsfile.put()
            
    @classmethod
    def get_gsfile_by_user(cls,user):
        return GSFile.all().filter('user =',user).order('-created')
        
if __name__=='__main__':
    pass