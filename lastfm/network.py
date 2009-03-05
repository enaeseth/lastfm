# encoding: utf-8

"""
Handles the low-level details of communicating with last.fm over HTTP.
"""

from urllib import urlencode
import urllib2
from urlparse import urlparse, parse_qs, urlunparse
import sys

__version__ = '0.1'

def unparse_qs(params):
    return '&'.join('%s=%s' % (k, urlencode(v)) for k, v in params.iteritems())

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
            data = unparse_qs(data)
        
        return self._opener.open(url, data)
        
    def _add_params(self, url, params):
        """Appends GET parameters to the URL and returns the result."""
        
        parsed = urlparse(url)
        url_params = parse_qs(parsed.query)
        url_params.update(params)
        parsed.query = unparse_qs(url_params)
        
        return urlunparse(parsed)

    @property
    def _user_agent(self):
        return 'Python-Last.fm-Client/%s (Python-urllib/%s; %s)' % (
            __version__,
            sys.platform.capitalize(),
            urllib2.__version__
        )