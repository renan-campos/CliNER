import cPickle as pickle 
import os

class UmlsCache:
    def __init__(self):
        try:
            prefix = os.environ['CLICON_DIR']
            self.filename = os.path.join( prefix, 'umls_tables/umls_cache' )
            self.cache = pickle.load( open( self.filename , "rb" ) ) ;
        except IOError:

            print "NO CACHE"
            self.cache = {} 
    
    def has_key( self , string ): 
        return self.cache.has_key( string )  

    def add_map( self , string, mapping ):
        self.cache[string] = mapping 

    def get_map( self , string ):
        return self.cache[string] 
 
    def __del__(self):  
        pickle.dump( self.cache, open( self.filename, "wb" ) )    
