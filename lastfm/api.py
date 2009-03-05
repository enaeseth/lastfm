# encoding: utf-8

"""
Provides access to the last.fm API.
"""

try:
    import json
except ImportError:
    import simplejson as json
    
from lastfm.caching import local
from lastfm.network import Agent

class Client(object):
    """
    A last.fm API client.
    
    All access to the API must go through a Client object.
    All API requests are synchronus.
    """
    
    def __init__(self, api_key, secret=None, cache=None, agent=None):
        """
        Creates a new last.fm API client.
        
        The `api_key` is your application's API key. An API key must be obtained
        from last.fm before the API can be used by any means (including via
        this library).
        
        The `secret` is your application's secret key. This key
        is only used in requests that require authorization.
        
        The `cache` parameter can be set to a cache object which will be used to
        cache results from the last.fm service. This can be any object which
        support dictionary-style access with string keys: cache[key] must return
        the object associated with the key if it is cached, or None if it is not
        in the cache; and cache[key] = obj must store `obj` in the cache under
        `key` for a period of time. Two implementations are bundled:
        lastfm.caching.local.Cache is a local, dictionary-based cache, and
        lastfm.caching.memcache.Cache uses memcached as a backing. If `cache` is
        None, a default local cache will be used. If `cache` is False, no cache
        will be used.
        
        The `agent` parameter specifies an agent object used for making HTTP
        requests. If set to None, a live, urllib2-based implementation will be
        used. Changing the agent is mostly useful for testing.
        """
        
        if not api_key:
            raise ValueError("cannot create a client with no API key")
        
        self._key = api_key
        self._secret = secret
        
        if cache is False:
            self._cache = self._BlackHoleCache()
        elif cache is None:
            self._cache = local.Cache()
        else:
            self._cache = cache
            
        self._agent = agent or Agent()
        
    @property
    def api_key(self):
        """The API key used by the client."""
        return self._key
        
    @property
    def secret(self):
        """The secret key used by the client."""
        return self._secret
        
    @property
    def cache(self):
        """The object cache used by the client."""
        return self._cache
        
    @property
    def agent(self):
        """The HTTP request agent used by the client."""
        return self._agent
        
    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self._key)
        
    class _BlackHoleCache(object):
        """A black hole: a cache that stores nothing."""
        
        def __getitem__(self, key):
            return None

        def __setitem__(self, key, value):
            pass

        def __delitem__(self, key):
            pass

        def __contains__(self, key):
            return False


