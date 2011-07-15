# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Low-level module for connecting to the Rexster REST server and
returning a Response object.

"""

import urllib
import urllib2
import httplib2
import simplejson as json
from urlparse import urlsplit
from posixpath import basename
import config

DEBUG = config.DEBUG
MAX_RETRIES = config.MAX_RETRIES

class Resource(object):
    """Used for connecting to the Rexster REST server."""

    def __init__(self,db_url):
        """
        Initializes a resource object.

        :param db_url: the base URL of Rexster.

        """
        self.db_url = db_url
        if db_url.endswith("/"):
            # strip off trailing slash
            db_url = db_url[:-1]
        url_object = urlsplit(db_url)
        self.base_url = "%s://%s" % (url_object.scheme,url_object.netloc)
        self.db_name = basename(url_object.path)        

    def get(self,target,params):
        """Convenience method that sends GET requests to the resource.""" 
        return self.request("GET",target,params)
       
    def post(self,target,params):
        """Convenience method that sends POST requests to the resource."""
        return self.request("POST",target,params)
    
    def delete(self,target,params):
        """Convenience method that sends DELETE requests to the resource."""
        return self.request("DELETE",target,params)
    
    def request(self, method, target, params):
        """
        Sends requests to the resource.

        :param method: either GET, POST, or DELETE.
        :param target: the URL path relative to the database URL you specified 
                       in either config.py or that you passed in as an argument
                       when you instantiated the resource.
        :param params: a dict of query-string parameters to include in the URL 
        """

        assert method in ("GET","POST","DELETE"), \
            "Only GET, POST, DELETE are allowed."

        headers = {'Accept': 'application/json'}

        # httplib2 let's you cache http responses with memcache 
        # really cool, look into that later
        # http = httplib2.Http(memcache)

        # the indicies condition is a hack until you implement 
        # list type for indices keys
        if params and method is "POST" and "indices" not in target:
            url = self._build_url(method, target, params=None)
            body = urllib.urlencode(params)
            post_headers = {'Content-type': 'application/x-www-form-urlencoded'}
            headers.update(post_headers)
        else:
            url = self._build_url(method, target, params)
            body = None
                
        if DEBUG:
            print "REST url:  ", url
            print "REST body: ", body

        attempt = 0
        ok = False
        http = httplib2.Http()       
        while not ok and (attempt < MAX_RETRIES):
            resp = Response(http.request(url, method, body, headers))
            attempt += 1
            ok = resp.ok            

        # TODO: check http_status for 401s
        #assert resp.ok == True

        # TODO: if resp.http_status == 200, 
        # else (where to put this?...maybe better at a higher level)

        return resp
    
    def _build_url(self, method, target, params):
        """Used internally to construct the complete URL to the service."""
        if type(target) == unicode:
            target = target.encode("utf8")
        url = "%s/%s" % (self.base_url, urllib2.quote(target)) 
        if params:            
            url = "%s?%s" % (url, urllib.urlencode(params))
        return url
            
        
class Response(object):
    """A container for the Rexster HTTP response."""

    def __init__(self, http_resp):
        """
        NOTE: headers is a httplib2 Response object, content is a string
        see http://httplib2.googlecode.com/hg/doc/html/libhttplib2.html
        """
        headers, content = http_resp
        self._response_handler(headers)
        if DEBUG:
            # only set raw if DEBUG=True to save on memory
            self.raw = http_resp
        try:
            self.headers = headers
            # don't save content on the resp object else you'll bloat it
            content = json.loads(content)
            self.ok = True

            # true if he response was returned from the cache
            self.fromcache = headers.fromcache
            
            # version of HTTP that the server supports. A value of 11 means 1.1
            self.http_version = headers.version
            
            # numerical HTTP status code returned in the response
            self.http_status = headers.status
            
            # human readable component of the HTTP response status code
            self.http_reason = headers.reason

            # previous response object if redirects are followed
            self.http_previous = headers.previous
        
            #
            # header values not set in resp object but stored in the dict
            #
            # URI that was ultimately requested
            self.content_location = self.headers.get('content-location')
            self.tansfer_encoding = self.headers.get('transfer-encoding')
            self.server = self.headers.get('server')
            self.date = self.headers.get('date')
            self.allow_origin = self.headers.get('access-control-allow-origin')
            self.content_type = self.headers.get('content-type')
            
            #
            # body values always returned by reXster
            #            
            self.rexster_version = content.get('version')
            self.query_time = content.get('queryTime')
            if self.query_time:
                self.query_time = float(self.query_time)
 
            #
            # body values sometimes returned, depending on resource requested
            #
            # if results is returned, it's a list of dicts, and
            # the dicts can contain any number of key/value pairs depending on 
            # what is stored in each item -- items can be a node,edge...
            self.success = bool(content.get('success'))
            if "results" in content and type(content['results']) == list:
                self.results = iter(content['results'])
            else:
                self.results = content.get('results')
            self.index_name = content.get('name')
            self.index_class = content.get('class')
            self.index_type = content.get('type')            
            self.total_size = content.get('totalSize')

        except ValueError:
            # looks like this isn't json, data is None
            self.ok = False

    def _response_handler(self,headers):
        """TODO: handle response errors.""" 
        # Is there a list of error codes Rexster sends?
        # Putting this in element won't work b/c element doesn't get the full 
        # resp anymore, just results. Prob relegate to an resp/error helper
        pass

