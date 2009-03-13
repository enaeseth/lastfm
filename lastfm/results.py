# encoding: utf-8

"""
Data types that represent last.fm search results.
"""
    
from lastfm.errors import APIError

class SearchResult(list):
    """
    A last.fm search result.
    
    Last.fm returns search results in paginated form. Since results are returned
    in order of relevance, you may not need more than the first page, but if
    you do, instances of this class allow you to load further pages and see how
    many items matched total.
    """
    
    def __init__(self, loader, result_field, converter):
        """
        Constructs a new search result from JSON-decoded search results.
        """
        
        self._total_results, raw = read_search_results(loader(1),
            result_field)
        super(SearchResult, self).__init__(converter(e) for e in raw)
        
        self._result_field = result_field
        self._converter = converter
        self._loader = loader
        self._last_page = 1
        
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
        
        results = self._loader(self._last_page + 1)
        self._total_results, new_results = read_search_results(results,
            self._result_field)
        self.extend(map(self._converter, new_results))
        self._last_page += 1
        return len(new_results)
        
    def __repr__(self):
        return '<SearchResult %s>' % super(SearchResult, self).__repr__()
        
def read_search_results(data, result_field):
    """
    Reads the search results from the stream, and returns a pair: the total
    number of results produced by the search, and the search results on this
    page.
    """
    
    if 'error' in data:
        raise APIError(data['message'], int(data['error']))
    
    results = data['results']
    
    match_field = '%smatches' % result_field
    return (int(results['opensearch:totalResults']),
        results[match_field][result_field])
