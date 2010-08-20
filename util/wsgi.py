#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/12 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""
from google.appengine.ext.webapp import *


class XFoxWSGIApplication(WSGIApplication):
    '''
    xFox WSGI Application
    '''
    def __call__(self, environ, start_response):
        """Called by WSGI when a request comes in."""
        request = self.REQUEST_CLASS(environ)
        response = self.RESPONSE_CLASS()

        WSGIApplication.active_instance = self

        handler = None
        groups = ()
        for regexp, handler_class in self._url_mapping:
            match = regexp.match(request.path)
            if match:
                handler = handler_class()
                handler.initialize(request, response)
                groups = match.groups()
                break

        self.current_request_args = groups
        if handler:
            try:
                method = environ['REQUEST_METHOD']
                if method == 'GET':
                    handler.get(*groups)
                elif method == 'POST':
                    handler.post(*groups)
                elif method == 'HEAD':
                    handler.head(*groups)
                elif method == 'OPTIONS':
                    handler.options(*groups)
                elif method == 'PUT':
                    handler.put(*groups)
                elif method == 'DELETE':
                    handler.delete(*groups)
                elif method == 'TRACE':
                    handler.trace(*groups)
                else:
                    handler.error(501)
            except Exception, e:
                    handler.handle_exception(e, self.__debug)
        else:
            response.set_status(404)

        response.wsgi_write(start_response)
        return ['']
    
def webapp_add_wsgi_middleware(app):
    return app
    #from google.appengine.ext.appstats import recording
    #app = recording.appstats_wsgi_middleware(app)
    #return app

if __name__=='__main__':
    pass