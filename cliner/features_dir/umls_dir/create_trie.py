#database.py creates a .db file for performing umls searches.
import marisa_trie
import sys
import os
import cPickle as pickle



def back(path):
    return os.path.dirname(path)



def create_trie():

    """
    create_trie()

    Purpose: Build a trie of concepts from MRREL

    @return  A trie object
    """

    # Is trie already built & pickled?
    prefix = back(back(back(__file__)))
    filename = os.path.join( prefix, 'umls_tables/umls-concept.trie' )
    try:
        t = pickle.load( open( filename , "rb" ) ) ;
        return t
    except IOError:
        pass


    print "\ncreating concept-trie"

    #load data in files.
    print "opening file"
    try:
        mrcon_path = os.path.join(prefix,'umls_tables/MRCON')
        MRCON_TABLE = open( mrcon_path , "r" )
    except IOError:
        print "\nNo file to use for creating MRCON table\n"
        conn.close()
        sys.exit()


    print "reading file"
    MRCON_TABLE = MRCON_TABLE.read()
    MRCON_TABLE = MRCON_TABLE.split( '\n' )

    #data that will be inserted into tables.
    MRCON_DATA = []

    print "parsing file"

    #parse and store the data from the files.
    for line in MRCON_TABLE:
        MRCON_DATA.append( tuple(line.split('|')) )

    #insert data onto database
    print "inserting data"
    concepts = []
    for line in MRCON_DATA:
        if len(line) < 6: continue

        concept = line[6]

        # Ignore non-ascii
        try:
            concept.decode('ascii')
        except:
            continue

        #print type(concept)
        concepts.append(concept)


    print "creating trie"
    t = marisa_trie.Trie(concepts)

    print "concept-trie created"


    # Pickle trie
    pickle.dump( t, open( filename, "wb" ) )

    return t


if __name__ == '__main__':
    t = create_trie()
