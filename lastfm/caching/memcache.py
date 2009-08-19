# encoding: utf-8

"""
Provides a memcached-backed cache class that can be used with the Last.fm API
module.
"""

from __future__ import absolute_import

try:
    import cmemcache as _memcache
except ImportError:
    try:
        import memcache as _memcache
    except ImportError:
        raise ImportError("No memcache implementation module found "
            "(tried cmemcache and memcache)")

import re

class Cache(object):
    """
    A memcached-backed cache that can be used with the Last.fm API module. Items
    in the cache can be retrieved, set, and deleted using dictionary style
    access. For example:
    
        cache = Cache("127.0.0.1:11211")
        cache["foo"] = "bar"
        stored_val = cache["foo"]
        del cache["foo"]
    """
    
    _control_chars = re.compile(r'[\x00-\x21\x7f]+')
    
    def __init__(self, servers, format=None, timeout=600):
        """
        Creates a new memcached-backed cache.
        
        The `servers` parameter should be a list of locations of memcached
        servers. To contact a server over IP, give its location in "host:port"
        format; to contact one over a UNIX socket, give the absolute path to the
        socket. To distribute the load over servers differently, entries in the
        `servers` list can be tuples of which the first item is the location
        and the second item is an integer weight. Servers default to a weight
        of 1. If only one server is being used, it is acceptable to provide its
        location string as `servers`.
        
        The `format` string, if given, should be a format string suitable for
        the string interpolation operator (%). For example, to prefix "lastfm_"
        to all keys before they are transmitted to memcached, set format to
        "lastfm_%s". Defaults to "%s" (i.e., no modification).
        
        The `timeout` parameter gives the time to live for items in this cache
        in seconds.
        """
        
        self._format = format or '%s'
        self._timeout = timeout
        
        if isinstance(servers, basestring):
            servers = [servers]
        self._client = _memcache.Client(servers, debug=0)
        
    def _expand_key(self, key):
        clean_key = self._control_chars.sub('_', key).lower()
        return (self._format % clean_key).encode('UTF-8')
        
    def __getitem__(self, key):
        return self._client.get(self._expand_key(key))
        
    def __setitem__(self, key, value):
        self._client.set(self._expand_key(key), value, self._timeout)
        
    def __delitem__(self, key):
        self._client.delete(self._expand_key(key))
        
    def __contains__(self, key):
        return self[key] is not None
