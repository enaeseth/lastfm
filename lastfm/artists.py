# encoding: utf-8

"""
Types that represent last.fm artist data.
"""

from lastfm.errors import APIError, UnderspecifiedError
from lastfm.results import SearchResult
from lastfm.data import *

class Artist(SmartData):
    """
    Represents an artist in the last.fm database.
    """
    
    def __init__(self, client, name=None, id=None, url=None):
        super(Artist, self).__init__(client)
        if name:
            self._name = name
        if id:
            self._id = id
        if url:
            self._url = url
    
    _fields = (
        ("name", None),
        ("mbid", None, "_id"),
        ("bio", WikiEntry.from_row, "_biography"),
        ("image", lambda lst: [Image.from_row(i) for i in lst], "_images"),
        ("stats", lambda s: dict((k, int(v)) for k, v in s.iteritems())),
        ("streamable", lambda v: bool(int(v))),
        ("url", None)
    )
    
    @property
    def name(self):
        """The name of the artist."""
        return self._name
    
    @smart_property
    def id(self):
        """The MusicBrainz UUID of the artist."""
        return self._id
    
    @smart_property
    def biography(self):
        """The Wiki entry representing the artist's biography."""
        return self._biography
    
    @smart_property
    def images(self):
        """Images of the artist."""
        return self._images
    
    @smart_property
    def stats(self):
        """Listening statistics for the artist."""
        return self._stats
    
    @smart_property
    def streamable(self):
        """Whether or not the artist can be streamed via last.fm."""
        return self._streamable
    
    @smart_property
    def url(self):
        """The URL of the last.fm page for this artist."""
        return self._url
        
    @cached_result('similar_artists:{name}')
    def get_similar(self):
        """Gets artists that are similar to this artist."""
        raw = self._client.raw.artist.get_similar(artist=self._name)
        artists = raw['similarartists']['artist']
        
        matches = []
        for artist in artists:
            match = float(artist.pop('match'))
            matches.append((match, Artist.from_row(self._client, artist)))
        return matches
    
    @property
    @cached_result('top_albums:{name}')
    def top_albums(self):
        """The top-played albums by this artist on last.fm."""
        from lastfm.albums import Album
        
        raw = self._client.raw.artist.get_top_albums(artist=self._name)
        rows = raw['topalbums']['album']
        
        return [Album.from_row(self._client, row) for row in rows]
    
    def _load_info(self):
        spec = (self._id and dict(mbid=self._id)) or dict(artist=self._name)
        self._add_data(self.fetch_row(self._client, spec))
        
    @classmethod
    def fetch_row(cls, client, spec, no_redirect=False):
        cached = client._cache_find('artist', spec.get('mbid'),
            spec.get('artist'))
        if cached:
            return cached
        
        fresh = client.raw.artist.get_info(**spec)['artist']
        
        if not no_redirect and '+noredirect' in fresh['url']:
            # Pick the first similar artist as the correct spelling.
            if fresh['similar'] and fresh['similar']['artist']:
                correct = fresh['similar']['artist'][0]
                spec = {'artist': correct['name']}
                fresh = cls.fetch_row(client, spec, no_redirect)
        
        client.cache['artist:%s' % fresh['name']] = fresh
        if 'mbid' in fresh:
            client.cache['artist:%s' % fresh['mbid']] = fresh
        return fresh
        
    def __repr__(self):
        id_str = (self._id and ' (%s)' % self._id) or ''
        return '<%s "%s"%s>' % (type(self).__name__, self.name, id_str)
        
    def __unicode__(self):
        id_str = (self._id and ' (%s)' % self._id) or ''
        return u'<%s "%s"%s>' % (type(self).__name__, self.name, id_str)
    
class ArtistCollection(Collection):
    """
    Gives access to last.fm artist information.
    """
    
    def get(self, name=None, id=None, no_redirect=False):
        """
        Gets the information for the given artist. Set the `name` parameter to
        search by name; set the `id` parameter to search by MusicBrainz ID.
        
        This functon will automatically try to detect when the requested name
        is a misspelling, and will request the correct artist. To override this
        behavior, set `no_redirect` to a true value. The spelling correction, if
        used, will be stored in the cache.
        """
        
        spec = {}
        if name:
            spec['artist'] = name
        if id:
            spec['mbid'] = id
        if not spec:
            raise UnderspecifiedError('a name and/or a MBID is required')
        
        return Artist.from_row(self._client,
            Artist.fetch_row(self._client, spec, no_redirect))

    def search(self, name):
        """
        Searches last.fm for artists that match the given `name`.
        """
        
        client = self._client
        def retrieve_page(page):
            cached = client._cache_find('artist_search', '%s:%d' % (name, page))
            if cached:
                return cached
            
            result = client.raw.artist.search(artist=name, page=page)
            client.cache['artist_search:%s:%d' % (name, page)] = result
            return result
            
        def match_to_artist(match):
            return Artist.from_row(self._client, match)
        
        return SearchResult(retrieve_page, 'artist', match_to_artist)
