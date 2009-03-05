# encoding: utf-8

"""
Provides a local, dictionary-backed cache that can be used with the Last.fm API
module.
"""

from time import time

class Cache(object):
    """
    A local, dictionary-backed cache that can be used with the Last.fm API
    module.
    """
    
    def __init__(self, timeout=600):
        """
        Creates a new local cache.
        
        The `timeout` parameter is the number of seconds that an item can
        live in the cache before expiring.
        """
        self._store = {}
        self._timeout = timeout
        
    def __getitem__(self, key):
        try:
            item, expiration = self._store[key]
            return (expiration <= time() and item) or None
        except KeyError:
            return None
        
    def __setitem__(self, key, value):
        self._store[key] = (value, time() + self._timeout)
        
    def __delitem__(self, key):
        try:
            del self._store[key]
        except KeyError:
            pass
        
    def __contains__(self, key):
        try:
            item, expiration = self._store[key]
            return (expiration <= time())
        except KeyError:
            return False
