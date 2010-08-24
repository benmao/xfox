#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/9 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import settings
import logging

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import urlfetch

from boto.gs.connection import GSConnection

from util.decorator import mem
from account.models import User
from dash.models import Counter

def save_image_to_gs(key_name,bf,mime="image/png"):
    try:
        conn = GSConnection(gs_access_key_id = settings.gs_access_key_id,gs_secret_access_key =settings.gs_secret_access_key)
        bucket = conn.get_bucket(settings.bucket_name)
        gs_file = bucket.new_key(key_name)
        gs_file.set_contents_from_string(bf,policy="public-read",headers={"Content-Type":mime})
    except:
        return False
    return True

def get_latex_img(value):
    try:
        url = "http://latex.codecogs.com/png.latex?%s" % value
        logging.info(url)
        result = urlfetch.fetch(url)
        if result.status_code ==200:
            return result.content
        return None
    except:
        return None
    

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

        if img.height > 800: #need resize
            img.resize(width=800)
            #img.im_feeling_lucky()
            save_image_to_gs('s/'+key_name,img.execute_transforms(output_encoding=images.PNG))
            gsfile.small_pic='s/'+key_name
        if save_image_to_gs(key_name,bf,gsfile.mime):
            gsfile.put() 
            
    @classmethod
    def get_gsfile_by_user(cls,user):
        return GSFile.all().filter('user =',user).order('-created')

class LatexImage(db.Model):
    
    latex_str = db.TextProperty()    
    created = db.DateTimeProperty(auto_now_add = True)
    cname = db.StringProperty()
    
    is_done = db.BooleanProperty(default=False)
    
    @property
    def url(self):
        return "%s/latex/%s" %(self.cname,self.key().name())
    
    @classmethod
    def new(cls,latex_str,md5_str):
        latex = LatexImage.get_by_key_name(md5_str)
        if latex is None:
            latex = LatexImage(key_name = md5_str,latex_str=latex_str,cname = settings.cname)
            latex.put()
        if  not latex.is_done:
            #handle get image
            img = get_latex_img(latex_str)
            if not img is None: #save image to db
                if save_image_to_gs('latex/%s' % md5_str,img):
                    latex.is_done=True
                    latex.put()
        return True
    
    @classmethod
    def get_by_key(cls,key):
        @mem("latex:%s" % key)
        def _x(latex):
            return latex
        latex = LatexImage.get_by_key_name(key)
        if latex and latex.is_done:
            return _x(latex)
        return None
            
    
        
if __name__=='__main__':
    pass