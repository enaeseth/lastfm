# encoding: utf-8

"""
Data types that represent last.fm search results.
"""

try:
    import json
except ImportError:
    import simplejson as json
    
from lastfm.errors import APIError

class SearchResult(list):
    """
    A last.fm search result.
    
    Last.fm returns search results in paginated form. Since results are returned
    in order of relevance, you may not need more than the first page, but if
    you do, instances of this class allow you to load further pages and see how
    many items matched total.
    """
    
    def __init__(self, stream, result_field, converter, agent, source_url):
        """
        Constructs a new search result from an opened stream of search results.
        The stream will be closed by the time __init__ returns.
        """
        
        try:
            self._total_results, raw = read_search_results(stream, result_field)
            super(SearchResult, self).__init__(converter(e) for e in raw)
            self._agent = agent
            self._result_field = result_field
            self._converter = converter
            self._source = source_url
            self._last_page = 1
        finally:
            stream.close()
        
    @property
    def total_length(self):
        """The total number of items that resulted from the search."""
        return self._total_results
    
    def load_next_page(self):
        """
        Loads the next page of search results, and returns the number of new
        results that were produced.
        """
        
        if len(self) >= self.total_length: # already done
            return 0
        
        try:
            stream = self._agent.get(self._source,
                {'page': self._last_page + 1})
            self._total_results, new_results = read_search_results(stream,
                self._result_field)
            self.extend(map(self._converter, new_results))
            self._last_page += 1
            return len(new_results)
        finally:
            stream.close()
        
    def __repr__(self):
        return '<SearchResult %s>' % super(SearchResult, self).__repr__()
        
def read_search_results(stream, result_field):
    """
    Reads the search results from the stream, and returns a pair: the total
    number of results produced by the search, and the search results on this
    page.
    """
    
    data = json.load(stream)
    
    if data['error']:
        raise APIError(data['message'], int(data['error']))
    
    results = data['results']
    
    return (int(results['opensearch:totalResults']), results[result_field])