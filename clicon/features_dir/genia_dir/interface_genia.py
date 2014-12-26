######################################################################
#  CliCon - clicon_genia_interface.py                                #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Provide a way for Python to utilize the output of the    #
#               GENIA Tagger                                         #
#                                                                    #
#  Genia Tagger: http://www.nactem.ac.uk/tsujii/GENIA/tagger/        #
######################################################################



__author__ = 'Willie Boag'
__date__   = 'Jan. 27, 2014'

import os
import sys
from commands import getstatusoutput

from genia_cache import GeniaCache



def genia(geniatagger, data):

 #   print "called genia"

    '''
    genia()

    Purpose: Call the genia tagger and return its output in python format

    @param geniatagger.  A path to the executable geniatagger
    @param data.         A list of list of strings (lines of words from a file)
    @return              A list of dcitionaries of the genia tagger's output.
    '''

    # Lookup cache
    cache = GeniaCache()

    # Get uncached lines
    uncached = []
    for line in data:
        sent = ' '.join(line)
        if not cache.has_key(sent):
            uncached.append(sent)

    if uncached:
        # write list to file and then feed it to GENIA
        genia_dir = os.path.dirname(geniatagger)
        out = os.path.join(genia_dir,'clicon_genia_tmp_file.txt')
        with open(out, 'w') as f:
            for line in uncached: f.write(line + '\n')

        # Run genia tagger
        print '\t\tRunning  GENIA tagger'
        genia_dir = os.path.dirname(geniatagger)
        stream = getstatusoutput('cd %s ; ./geniatagger -nt %s' %(genia_dir,out))

        print '\t\tFinished GENIA tagger'

        # Organize tagger output
        linetags = []
        tagged = []
        for tag in stream[1].split('\n')[4:]:
            if tag.split():               # Part of line
                linetags.append(tag)
            else:                         # End  of line
                tagged.append(linetags)
                linetags = []

        # Add tagger output to cache
        for line,tags in zip(uncached,tagged):

            cache.add_map(line,tags)

        # Remove temp file
        os.remove(out)


    # Extract features
    linefeats = []
    retlist = []
    for line in data:
        line = ' '.join(line)

        # Get tagged output from cache
        tags = cache.get_map(line)

        # Some tokenized sentences are very long
        if tags and 'warning: the sentence seems to be too long' in tags[0]:
            tags = tags[1:]

        for tag in tags:
            tag = tag.split()
            output = { 'GENIA-word'    : tag[0] ,
                       'GENIA-stem'    : tag[1] ,
                       'GENIA-POS'     : tag[2] ,
                       'GENIA-chunktag': tag[3] ,
                       'GENIA-NEtag'   : tag[4] }
 
            linefeats.append(output)

        retlist.append(linefeats)
        linefeats = []


#    print retlist
    return retlist




if __name__ == '__main__':
    main()
