# encoding: utf-8

"""
Common data types used elsewhere in the library.
"""

from email.utils import parsedate
from datetime import datetime

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
        """The image's size (small, medium, or large)."""
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
        def add(prop, converter=None, dest=None):
            if not dest:
                dest = '_%s' % prop
            
            if prop in row:
                if not converter:
                    converter = lambda v: v # identity function
                setattr(self, dest, converter(row[prop]))
            elif not hasattr(self, dest):
                setattr(self, dest, None)
                
        for spec in self._fields:
            if len(spec) > 2:
                dest = spec[2]
            else:
                dest = None
            
            add(spec[0], spec[1], dest)
        
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
    
    def load_if_needed(self, *args, **kwargs):
        result = callable(self, *args, **kwargs)
        if result is not None:
            return result
        
        self._load_info()
        return callable(self, *args, **kwargs)
    
    load_if_needed.__doc__ = callable.__doc__
    return load_if_needed

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
