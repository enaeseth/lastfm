Last.fm API for Python
======================

A nascent library for using the [last.fm][lastfm] API from Python. This library
is still in development: only one API method (`artist.getInfo`) is fully
implemented. But the example usage should give a good idea of how easy it will
be to use this library:

    #!/usr/bin/env python
    
    import lastfm
    
    client = lastfm.Client("[your API key]")
    diva = client.artists.get('Madonna')
    
    # `diva` is now full of information on Madonna

[lastfm]: http://www.last.fm/
