# encoding: utf-8

"""
Common data types used elsewhere in the library.
"""

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
