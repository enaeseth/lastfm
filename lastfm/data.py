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
    
    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.url, self.size)
    
    def __eq__(self, other):
        if not isinstance(other, Image):
            return False
        return other.url == self.url and other.size == self.size

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
