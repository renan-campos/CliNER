

__author__ = 'Willie Boag'
__date__   = 'Dec. 26, 2014'


import os
import re
import cPickle as pickle
import urllib2
from BeautifulSoup import BeautifulSoup

import helper



def back(path):
    return os.path.dirname(path)



class UmlsSimilarity:

    def __init__(self):
        # Ensure cache dir exists
        BASE_DIR = back(back(back(__file__)))
        cache_dir = os.path.join(BASE_DIR, 'caches')
        helper.mkpath(cache_dir)

        # Read data
        self.filename = os.path.join(cache_dir, 'url.cache')
        try:
            with open(self.filename,'r') as f:
                self.cache = pickle.load(f)
        except IOError:
            self.cache = {}

        self.new = {}


    def normalizeKey(self,term1, term2):
        return (term1,term2)


    def distance(self, term1, term2):
        key = self.normalizeKey(term1,term2)

        # Cached?
        if key in self.cache:
            return self.cache[key]
        if key in self.new:
            return self.new[key]

        print 'querying: ', key

        # Build URL for web query
        url = ('http://atlas.ahc.umn.edu/cgi-bin/umls_similarity.cgi?word1=' +
               term1 + '&word2=' + term2 +
               '&sab=MSH&rel=PAR%2FCHD&similarity=path&button=Compute+Similarity&sabdef=UMLS_ALL&reldef=CUI%2FPAR%2FCHD%2FRB%2FRN&relatedness=vector')


        uf = urllib2.urlopen(url)
        html = uf.read()

        #print html

        match = re.search('using Path Length \(path\) is (\d+)', html)

        #print 'match: ', match

        if match:
            score = match.group(1)
        else:
            score = 10**10

        self.new[key] = score

        return score


    def __del__(self):

        # Do not dump pickle if no new data
        if self.new:
            # Save cache
            self.cache.update(self.new)
            with open(self.filename,'w') as f:
                pickle.dump(self.cache, f)



def main():

    term1 = 'blood'
    term2 = 'blood'

    sim = UmlsSimilarity()

    print sim.distance(term1,term2)




if __name__ == '__main__':
    main()
