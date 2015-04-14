import cPickle as pickle
import os



def back(path):
    return os.path.dirname(path)


class UmlsCache:
    def __init__(self):
        try:
            prefix = back(back(back(__file__)))
            self.filename = os.path.join( prefix, 'umls_tables/umls_cache' )
            self.cache = pickle.load( open( self.filename , "rb" ) ) ;
        except IOError:
            self.cache = {}

    def has_key( self , string ):
        return self.cache.has_key( string )

    def add_map( self , string, mapping ):
        self.cache[string] = mapping

    def get_map( self , string ):
        return self.cache[string]

    def __del__(self):
        pickle.dump( self.cache, open( self.filename, "wb" ) )
