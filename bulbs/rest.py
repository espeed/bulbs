# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Low-level module for connecting to the Rexster REST server and
returning a Response object.

"""
import httplib2

import bulbs
from bulbs.base import Response
from .utils import json, get_logger, quote, urlencode


log = get_logger(__name__)

GET = "GET"
PUT = "PUT"
POST = "POST"
DELETE = "DELETE"

# HTTP Response Handlers
def ok(http_resp):
    return

def created(http_resp):
    return
    
def no_content(http_resp):
    return

def bad_request(http_resp):
    raise ValueError(http_resp)

def not_found(http_resp):
    raise LookupError(http_resp)
    #return None

def method_not_allowed(http_resp):
    # TODO: is there a better error for this than SystemError?
    raise SystemError(http_resp)

def conflict(http_resp):
    raise SystemError(http_resp)

def server_error(http_resp):
    raise SystemError(http_resp)

RESPONSE_HANDLERS = {200:ok,
                     201:created,
                     204:no_content,
                     400:bad_request,
                     404:not_found,
                     405:method_not_allowed,
                     409:conflict,
                     500:server_error}

# good posture good brain

class Request(object):
    """Used for connecting to the a REST server over HTTP."""

    response_class = Response

    def __init__(self, config, content_type):
        """
        Initializes a client object.

        :param root_uri: the base URL of Rexster.

        """
        self.config = config
        self.content_type = content_type
        self.user_agent = "bulbs/%s" % (bulbs.__version__)
        self.http = httplib2.Http()    
        self._add_credentials(config.username, config.password)
        self._initialize()

    def _initialize(self):
        pass
    
    def get(self, path, params=None):
        """
        Convenience method that sends GET requests to the client.

        :param path: Path to the server resource, relative to the root URI.
        :type path: str

        :param params: Optional URI params for the resource.
        :type params: dict

        :rtype: Response

        """ 
        return self.request(GET, path, params)

    def put(self, path, params=None):
        """
        Convenience method that sends PUT requests to the client.

        :param path: Path to the server resource, relative to the root URI.
        :type path: str

        :param params: Optional URI params for the resource.
        :type params: dict

        :rtype: Response

        """
        return self.request(PUT, path, params)

    def post(self, path, params=None):
        """
        Convenience method that sends POST requests to the client.

        :param path: Path to the server resource, relative to the root URI.
        :type path: str

        :param params: Optional URI params for the resource.
        :type params: dict

        :rtype: Response

        """
        return self.request(POST, path, params)

    def delete(self, path, params=None):
        """
        Convenience method that sends DELETE requests to the client.

        :param path: Path to the server resource, relative to the root URI.
        :type path: str

        :param params: Optional URI params for the resource.
        :type params: dict

        :rtype: Response

        """
        return self.request(DELETE, path, params)
    
    def send(self, message):
        """
        Convenience method that sends request messages to the client.

        :param message: Tuple containing: (HTTP method, path, params)
        :type path: tuple

        :param params: Optional URI params for the resource.
        :type params: dict

        :rtype: Response

        """
        method, path, params = message
        return self.request(method, path, params)

    def request(self, method, path, params):
        """
        Sends a request to the client.

        :param method: HTTP method: GET, PUT, POST, or DELETE.
        :type method: str

        :param path: Path to the server resource, relative to the root URI.
        :type path: str

        :param params: Optional URI parameters for the resource.
        :type params: dict

        :rtype: Response

        """
        uri, method, body, headers = self._build_request_args(path, method, params)

        self._display_debug(uri, method, body)

        http_resp = self.http.request(uri, method, body, headers)

        return self.response_class(http_resp, self.config)


    def _display_debug(self, uri, method, body):
        log.debug("%s url:  %s  ", method, uri)
        log.debug("%s body: %s ", method, body)
                    
    def _build_request_args(self, path, method, params):
        headers = {'Accept': 'application/json',
                   'User-Agent': self.user_agent}
        body = None

        uri = "%s/%s" % (self.config.root_uri.rstrip("/"), path.lstrip("/"))

        if params and method is GET:
            uri = "%s?%s" % (uri, urlencode(params))
        
        if params and (method in [PUT, POST, DELETE]):
            body = json.dumps(params)
            post_headers = {'Content-Type': self.content_type}
            headers.update(post_headers)
        
        return uri, method, body, headers 

    def _add_credentials(self, username, password):
        if username and password:
            self.http.add_credentials(username, password)

    # how to reuse the http object?
    def __getstate__(self):
        state = self.__data__.copy()
        del state['http']
        return state

    def __setstate__(self, state):
        state['http'] = httplib2.Http()
        self.__data__ = state

