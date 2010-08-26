#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/26 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

from discussion.models import Tag,Discussion
from util.paging import PagedQuery

cell_list = []
cell_dict={}

class Cell():
   NAME = 'cell'
   PAGESIZE = 15
   _template = {
      'list' : '',
      'post': '',
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
   def post(cls,request):
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
      'post': 'p.html',
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
      diss = Discussion.get_by_tag(tag)
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
   def post(cls,request):
      pass
   
   @classmethod
   def get(cls,request):
      pass
   
cell_list.append(DefaultCell)
cell_dict.update({DefaultCell.NAME:DefaultCell})

class ImageCell(Cell):
   NAME = 'img'
   PAGESIZE = 15
   _template = {
      'list' : 'tag_img.html',
      'post': 'p_img.html',
      'edit': 'p_edit_img.html',
      }

   @classmethod
   def tag_list(cls,request,tag):
      '''
      args:
      request:A webapp RequestHandler object
      tag : A tag object
      '''
      request.template_value['tag']=tag
      diss = Discussion.get_by_tag(tag)
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
      
cell_list.append(ImageCell)
cell_dict.update({ImageCell.NAME:ImageCell})

def get_cell(t):
   return cell_dict.get(t,DefaultCell)

if __name__=='__main__':
   pass