# encoding: utf-8

"""
Common data types used elsewhere in the library.
"""

from email.utils import parsedate
from datetime import datetime
import re

class Image(object):
    """An image served by last.fm."""
    
    def __init__(self, url, size):
        self._url = url
        self._size = size
        
    @property
    def url():
        """The image's URL."""
        return self._url
    
    @property
    def size():
        """The image's size (small, medium, large, or extralarge)."""
        return self._size
    
    @classmethod
    def from_row(cls, data):
        return cls(data['#text'], data['size'])
    
    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.url, self.size)
    
    def __eq__(self, other):
        if not isinstance(other, Image):
            return False
        return other.url == self.url and other.size == self.size
    

class WikiEntry(object):
    """An entry in the last.fm music wiki."""
    
    def __init__(self, summary, content, published):
        self._summary = summary
        self._content = content
        self._published = published
    
    @property
    def summary(self):
        """The summary of the wiki entry."""
        return self._summary
    
    @property
    def content(self):
        """The entry text."""
        return self._content
    
    @property
    def published(self):
        """The publication date and time as a datetime.datetime object."""
        return self._published
    
    @classmethod
    def from_row(cls, data):
        pubdate = data['published']
        published = (pubdate and parse_timestamp(data['published'])) or None
        return cls(data['summary'], data['content'], published)
    
    def __repr__(self):
        return '%s(%r, %r, %r)' % (type(self).__name__, self.summary,
            self.content, self.published)
    
    def __str__(self):
        return self.summary
    

class SmartData(object):
    """
    The base class for all last.fm data types for which not all the data is
    always immediately available (e.g., artists).
    """
    
    def __init__(self, client):
        self._client = client
        
        # Initialize fields.
        for spec in self._fields:
            dest = (len(spec) > 2 and spec[2]) or ('_%s' % spec[0])
            setattr(self, dest, None)
        
    @classmethod
    def from_row(cls, client, row):
        obj = cls(client)
        obj._add_data(row)
        return obj
        
    def _add_data(self, row):
        def add(prop, converter=None, dest=None, needs_client=False):
            if not dest:
                dest = '_%s' % prop
            
            value = row.get(prop)
            if isinstance(value, basestring):
                value = value.strip()
            
            if value:
                if not converter:
                    converter = lambda v: v # identity function
                elif needs_client:
                    orig_converter = converter
                    converter = lambda v: orig_converter(v, self._client)
                setattr(self, dest, converter(row[prop]))
            elif not hasattr(self, dest):
                setattr(self, dest, None)
                
        for spec in self._fields:
            if len(spec) > 2:
                dest = spec[2]
            else:
                dest = None
            
            needs_client = (len(spec) > 3 and spec[3]) or False
            
            add(spec[0], spec[1], dest, needs_client)
        
        return self
        
    def __getstate__(self):
        state = dict(self.__dict__)
        if '_client' in state:
            del state['_client']
        return state
        
def smart_property(callable):
    """
    Used to define a read-only property on a class that may not be immediately
    available.
    """
    
    loaded = [False]
    def load_if_needed(self, *args, **kwargs):
        result = callable(self, *args, **kwargs)
        
        if isinstance(result, (list, dict)):
            valid_result = len(result) > 0
        else:
            valid_result = result is not None
        
        if valid_result:
            return result
        
        self._load_info()
        loaded[0] = True
        return callable(self, *args, **kwargs)
    
    load_if_needed.__name__ = callable.__name__
    load_if_needed.__doc__ = callable.__doc__
    return property(load_if_needed)
    
_inline_attribute_pattern = re.compile(r'{(\w+)}')
def cached_result(cache_id, get_cache=None):
    """
    Used to define a method with results that are cached. The actual function
    will only be called to compute the results if the item is not in cache.
    
    The `cache_id` property gives the key under which the result is stored in
    the cache. It is possible to have parts of this ID string filled in with
    attributes from the object on which this property exists by enclosing them
    in curly braces ("{" and "}").
    
    This function is designed to be used as a decorator, e.g.:
    
        @cached_result("similar_artists:{name}")
        def get_similar(self):
            ...
    
    The cache must be accessible on the object on which this method appears
    through a Last.fm client in the _client attribute.
    """
    
    def default_cache_getter(obj):
        try:
            return obj._cache
        except AttributeError:
            try:
                return obj._client.cache
            except AttributeError:
                pass
            raise # raise the original error
    
    if not get_cache:
        get_cache = default_cache_getter
    
    def cache_callable(callable):
        def expand_key(obj):
            def get_attribute_value(match):
                return getattr(obj, match.group(1))
        
            return _inline_attribute_pattern.sub(get_attribute_value, cache_id)
    
        def get_cachable_value(self, *args, **kwargs):
            cache = get_cache(self)
            key = expand_key(self)
        
            value = cache[key]
            if value is None:
                value = cache[key] = callable(self, *args, **kwargs)
            return value
    
        get_cachable_value.__name__ = callable.__name__
        get_cachable_value.__doc__ = callable.__doc__
        return get_cachable_value
        
    return cache_callable

class Collection(object):
    """
    The base class for all collections of data made available through Client
    objects (e.g., artists, albums, etc.).
    """
    
    def __init__(self, client):
        """Creates a new collection object (internal use only)."""
        self._client = client
    
def parse_timestamp(stamp):
    """
    Parses an RFC822 timestamp as used by last.fm and returns a
    datetime.datetime object representing that time.
    """
    return datetime(*parsedate(stamp)[:6])

def handle_album_artist(info, client):
    """
    Creates an Artist object from the `artist` field on an album.
    """
    from lastfm.artists import Artist
    
    try:
        params = {
            'name': info.get('name'),
            'id': info.get('mbid'),
            'url': info.get('url')
        }
    except AttributeError:
        # `info` is a string giving the name of the artist
        params = dict(name=info)
    
    return Artist(client, **params)
