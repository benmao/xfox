#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/26 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
import logging
from discussion.models import Tag,Discussion
from util.paging import PagedQuery
from util.base import escape

cell_list = []
cell_dict={}

class Cell():
   NAME = 'cell'
   PAGESIZE = 15
   _template = {
      'list' : '',
      'add': '',
      'edit': '',
      }
   
   @classmethod
   def get_template_name(cls,t):
      '''
      Return Template Name
      '''
      assert t in cls._template
      return cls._template[t]

   @classmethod
   def tag_list(cls,request):
      '''
      Handle List Discussions
      args:
      request: A webapp RequestHandler object
      '''
      raise NotImplementedError()
   
   @classmethod
   def add(cls,request):
      '''
      Handle post a Discussion
      args:
      request: A webapp RequestHandler object
      '''
      raise NotImplementedError()
   
   @classmethod
   def edit(cls,request):
      '''
      Handle Edit Disscussion
      args:
      request:A webapp RequestHandler object
      '''
      raise NotImplementedError()

class DefaultCell(Cell):
   '''
   Default Handle for Discussion
   '''
   NAME = 'default'
   PAGESIZE = 15
   _template = {
      'list' : 'tag.html',
      'add': 'p.html',
      'edit': 'p_edit.html',
      }
   
   @classmethod
   def tag_list(cls,request,tag):
      '''
      args:
      request:A webapp RequestHandler object
      tag : A tag object
      '''
      request.template_value['tag']=tag
      diss = Discussion.get_by_tag(tag,cls.PAGESIZE)
      #paging
      p =  request.p
      prev = p -1 if p >1 else None
      tmp = diss.fetch_page(p)
      tnext = p+1 if len(tmp)== cls.PAGESIZE  else None
      request.template_value['prev'] = prev
      request.template_value['next'] = tnext
      request.template_value['diss'] = tmp
      request.template_value['f_tag'] = {'key':tag.key().name(),'title':tag.title,'show': 'G' in tag.role,'post':True} #only Public tag have feed 
      request.render(cls.get_template_name('list'))      
      
   @classmethod
   def add(cls,request,tag):
      '''
      args:
      request:A webapp RequestHandler object
      tag : A tag object
      '''
      def get(request,tag):
         request.template_value['tag']=tag
         request.render(cls.get_template_name('add'))
         
      def post(request,tag):
         title = request.request.get("title").strip()
         content = request.request.get("content")
         slug = request.request.get("slug","")
         
         kwargs = {
            'ip':request.request.remote_addr,
            'user_agent': escape(request.request.headers.get('User-Agent','Firefox')),
            'f':'M',
            }
         
         #Validate
         if len(title) >0 and len(content)>0:
            dis =Discussion.add(tag,slug,title,content,request.user,**kwargs)
            request.redirect(dis.url)
         request.template_value['error']=u"不要忘记标题或内容哦"
         request.template_value['tag']=tag
         request.template_value['title']=title
         request.template_value['content']=content
         request.render(cls.get_template_name('add')) 
      
      {'get':get,'post':post}.get(request.m)(request,tag)
   
   @classmethod
   def edit(cls,request,dis,*args,**kwargs):
      def get(request,tag,*args,**kwargs):
         request.template_value['dis']=dis
         request.render(cls.get_template_name('edit'))
         
      def post(request,dis,*args,**kwargs):
         title = request.request.get("title").strip()
         content = request.request.get("content")
      
         if len(title) >0 and len(content)>0:
            dis.title = title
            dis.content = content
            dis.put()
            request.redirect(dis.url)
         request.template_value['error']=u"不要忘记标题或内容哦"
         request.template_value['dis']=dis
         request.template_value['title']=title
         request.template_value['content']=content
         request.render(cls.get_template_name('edit')) 
         
      {'get':get,'post':post}.get(request.m)(request,dis,*args,**kwargs)
      
cell_list.append(DefaultCell)
cell_dict.update({DefaultCell.NAME:DefaultCell})

class ImageCell(Cell):
   NAME = 'img'
   PAGESIZE = 15
   _template = {
      'list' : 'tag_img.html',
      'add': 'p_img.html',
      'edit': 'p_edit.html',
      }

   @classmethod
   def tag_list(cls,request,tag):
      '''
      args:
      request:A webapp RequestHandler object
      tag : A tag object
      '''
      request.template_value['tag']=tag
      diss = Discussion.get_by_tag(tag,cls.PAGESIZE)
      #paging
      p =  request.p
      prev = p -1 if p >1 else None
      tmp = diss.fetch_page(p)
      tnext = p+1 if len(tmp)== cls.PAGESIZE  else None
      request.template_value['prev'] = prev
      request.template_value['next'] = tnext
      request.template_value['diss'] = tmp
      request.template_value['f_tag'] = {'key':tag.key().name(),'title':tag.title,'show': 'G' in tag.role,'post':True} #only Public tag have feed 
      request.render(cls.get_template_name('list'))        

   @classmethod
   def add(cls,request,tag):
      '''
      args:
      request:A webapp RequestHandler object
      tag : A tag object
      '''
      def get(request,tag):
         request.template_value['tag']=tag
         request.render(cls.get_template_name('add'))
         
      def post(request,tag):
         title = request.request.get("title").strip()
         content = request.request.get("content")
         slug = request.request.get("slug","")
         img_url = request.request.get("img_url")
         kwargs = {
            'ip':request.request.remote_addr,
            'user_agent': escape(request.request.headers.get('User-Agent','Firefox')),
            'f':'M',
            'img_url':img_url,
            }
         
         #Validate
         if len(title) >0 and len(content)>0:
            dis =Discussion.add(tag,slug,title,content,request.user,**kwargs)
            request.redirect(dis.url)
         request.template_value['error']=u"不要忘记标题或内容哦"
         request.template_value['tag']=tag
         request.template_value['title']=title
         request.template_value['content']=content
         request.template_value['img_url'] = img_url
         request.render(cls.get_template_name('add')) 
      
      {'get':get,'post':post}.get(request.m)(request,tag)
      
   @classmethod
   def edit(cls,request,dis,*args,**kwargs):
      DefaultCell.edit(request,dis,*args,**kwargs)
   
cell_list.append(ImageCell)
cell_dict.update({ImageCell.NAME:ImageCell})

def get_cell(t):
   return cell_dict.get(t,DefaultCell)

if __name__=='__main__':
   pass