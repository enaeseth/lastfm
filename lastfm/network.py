# encoding: utf-8

"""
Handles the low-level details of communicating with last.fm over HTTP.
"""

import urllib2
import sys

__version__ = '0.1'

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
        
    def open(url, data=None):
        """
        Opens an HTTP connection and sends a request.
        """
        return self._opener.open(url, data)

    @property
    def _user_agent(self):
        return 'Python-Last.fm-Client/%s (Python-urllib/%s; %s)' % (
            __version__,
            sys.platform.capitalize(),
            urllib2.__version__
        )