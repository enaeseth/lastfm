# encoding: utf-8

"""
Handles the low-level details of communicating with last.fm over HTTP.
"""

from urllib import urlencode
import urllib2
from urlparse import urlparse, urlunparse
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs
import sys
import re

try:
    import json
except ImportError:
    import simplejson as json
    
from lastfm.errors import APIError

__version__ = '0.1'
WS_ROOT = 'http://ws.audioscrobbler.com/2.0/'

class Agent(object):
    """
    Makes HTTP requests.
    """
    
    def __init__(self):
        """
        Creates a new request agent.
        """
        self._opener = urllib2.build_opener()
        self._opener.addheaders = [
            ('User-Agent', self._user_agent)
        ]
        
    def get(self, url, data=None):
        """
        Opens an HTTP connection and sends a GET request.
        The parameters in `params` are added as GET parameters.
        """
        return self._opener.open(self._add_params(url, data or {}))
        
    def post(self, url, data=None):
        """
        Opens an HTTP connection and sends a POST request.
        If `data` is a dictionary, it is first converted to URL-encoded
        parameters.
        """
        if isinstance(data, dict):
            data = urlencode(data)
        
        return self._opener.open(url, data)
        
    def _add_params(self, url, params):
        """Appends GET parameters to the URL and returns the result."""
        
        parsed = urlparse(url)
        url_params = parse_qs(parsed.query)
        url_params.update(params)
        parsed = list(parsed)
        parsed[4] = urlencode(url_params)
        
        return urlunparse(parsed)

    @property
    def _user_agent(self):
        return 'Python-Last.fm-Client/%s (Python-urllib/%s; %s)' % (
            __version__,
            sys.platform.capitalize(),
            urllib2.__version__
        )

class APIAccess(object):
    """
    Gives a natural way of making calls to the last.fm API.
    
    For example, if `api` is an APIAccess object, you can call the last.fm API
    method `artist.getInfo` via:
    
        api.artist.get_info(artist='Cher')
    """
    def __init__(self, key, agent):
        self._key = key
        self._agent = agent
        
    def __getattr__(self, name):
        return self.ModuleAccess(self._key, self._agent, name)
    
    class ModuleAccess(object):
        def __init__(self, key, agent, module):
            self._key = key
            self._agent = agent
            self._module = module
            
        def _translate_name(self, name):
            def change_underscore(match):
                return match.group(1) + match.group(2).upper()
            return re.sub(r'(.)_(.)', change_underscore, name)
            
        def __getattr__(self, name):
            def call_api(**kwargs):
                method = '.'.join([self._module, self._translate_name(name)])
                kwargs.update({
                    'api_key': self._key,
                    'method': method,
                    'format': 'json'
                })
                
                # XXX: a way to handle POST requests
                stream = self._agent.get(WS_ROOT, kwargs)
                try:
                    data = json.load(stream)
                    if 'error' in data:
                        raise APIError(data['message'], int(data['error']))
                    return data
                finally:
                    stream.close()
                
            call_api.__name__ = name
            return call_api
