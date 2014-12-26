import cPickle as pickle
import os

cacheDirPath = (os.environ["CLICON_DIR"]  +  "/clicon/features_dir/stanfordNLP/")

class DependencyCache:
    def __init__(self):
        try:
            self.filename = (cacheDirPath + '/dependency_cache')
            self.cache = pickle.load( open( self.filename , "rb" ) ) ;
        except IOError:
            self.cache = {}

    def has_key(self, key):
        return self.cache.has_key( str(key) )

    def add_map(self, key, value):
        self.cache[ str(key) ] = value

        pickle.dump( self.cache, open( self.filename, "wb" ) )

    def get_map(self, key):
        return self.cache[ str(key) ]

    def __del__(self):
        pickle.dump( self.cache, open( self.filename, "wb" ) )
