# encoding: utf-8

"""
Types that represent last.fm album data.
"""

from lastfm import artists
from lastfm.errors import APIError, UnderspecifiedError
from lastfm.results import SearchResult
from lastfm.data import *
from datetime import date
from email.utils import parsedate

class Album(SmartData):
    """
    Represents an album in the last.fm database.
    """
    
    def __init__(self, client, name=None):
        super(Album, self).__init__(client)
        if name:
            self._name = name
    
    _fields = (
        ("name", None),
        ("artist", handle_album_artist, "_artist", True),
        ("mbid", None, "_id"),
        ("releasedate", lambda v: date(*parsedate(v)[:3]),
            "_release_date"),
        ("wiki", WikiEntry.from_row, "_description"),
        ("image", lambda lst: [Image.from_row(i) for i in lst], "_images"),
        ("listeners", int),
        ("playcount", int, "_play_count"),
        ("toptags", handle_tags, "_tags"),
        ("url", None)
    )
    
    @property
    def name(self):
        """The name of the album."""
        return self._name
    
    @smart_property
    def id(self):
        """The MusicBrainz UUID of the album."""
        return self._id
    
    @smart_property
    def artist(self):
        """The artist who made this album."""
        return self._artist
    
    @smart_property
    def description(self):
        """The Wiki entry describing the album."""
        return self._description
    
    @smart_property
    def release_date(self):
        """The date the album was released as a datetime.date object."""
        return self._release_date
    
    @smart_property
    def images(self):
        """Images of the album (typically cover art)."""
        return self._images
    
    @smart_property
    def listeners(self):
        """The number of listeners this album has on last.fm."""
        return self._listeners
    
    @smart_property
    def play_count(self):
        """The number of times this album has been played on last.fm."""
        return self._play_count
    
    @smart_property
    def tags(self):
        """The top tags applied to this artist on last.fm."""
        return self._tags or []
    
    @smart_property
    def url(self):
        """The URL of the last.fm page for this album."""
        return self._url
    
    def _load_info(self):
        spec = (self._id and dict(mbid=self._id)) or dict(album=self._name,
            artist=self._artist.name)
        self._add_data(self.fetch_row(self._client, spec))
        
    @classmethod
    def fetch_row(cls, client, spec):
        if 'artist' in spec and 'album' in spec:
            criterion = "%s/%s" % (spec['artist'], spec['album'])
        else:
            criterion = spec.get('mbid')
        cached = client._cache_find('album', criterion)
        if cached:
            return cached
        
        fresh = client.raw.album.get_info(**spec)['album']
        
        qualified_name = "%s/%s" % (fresh['artist'], fresh['name'])
        client.cache['album:%s' % qualified_name] = fresh
        if 'mbid' in fresh:
            client.cache['album:%s' % fresh['mbid']] = fresh
        return fresh
    
    def __repr__(self):
        return str(unicode(self))
    
    def __unicode__(self):
        id_str = (self._id and ' (%s)' % self._id) or ''
        return u'<%s "%s" by "%s"%s>' % (type(self).__name__, self.name,
            (self.artist and self.artist.name), id_str)
    

class AlbumCollection(Collection):
    """
    Gives access to last.fm album information.
    """
    
    def get(self, name=None, artist=None, id=None):
        """
        Gets the information for the given album.
        
        Set the `artist and `name` parameters to search by name, or
        set `id` to search by MusicBrainz ID.
        """
        
        spec = {}
        if name and artist:
            spec['artist'] = artist
            spec['album'] = name
        if id:
            spec['mbid'] = id
        if not spec:
            raise UnderspecifiedError('an MBID or an artist and album name '
                'is required')
        
        return Album.from_row(self._client,
            Album.fetch_row(self._client, spec))
    
    def search(self, name):
        """
        Searches last.fm for albums with the given name.
        """
        
        client = self._client
        def retrieve_page(page):
            cached = client._cache_find('album_search', '%s:%d' % (name, page))
            if cached:
                return cached
            
            result = client.raw.album.search(album=name, page=page)
            client.cache['artist_search:%s:%d' % (name, page)] = result
            return result
            
        def match_to_album(match):
            return Album.from_row(self._client, match)
        
        return SearchResult(retrieve_page, 'album', match_to_album)
    
