from __future__ import with_statement


######################################################################
#  CliNER - abstract_note.py                                         #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Abstract Note representation.                            #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Nov. 6, 2014'



import re
import string
from copy import copy
import nltk.data
import os.path




# Abstract Note (to be inherited from)
class AbstractNote:

    def __init__(self):
        raise Exception('Cannot instantiate AbstractNote')


    ################################################################
    ####              Must support this interface              #####
    ################################################################

    def getExtension(self):
        """
        Purpose: Get the file extension for a particular format (ex. i2b2->con)
        """
        raise Exception('Must define getExtension() for derived class')


    def read(self, txt_file, con_file=None):
        """
        Purpose: Abstract method for reading data from file
        """
        raise Exception('Must define read() for derived class')


    def write(self, labels=None):
        """
        Purpose: Abstract method for writing data to file
        @param labels. A list of (concept,lineo,start_tok,end_tok) tuples
        """
        raise Exception('Must define write() for derived class')


    def getText(self):
        """
        Purpose: Return the verabitm string of text from text file
        """
        raise Exception('Must define selector for derived class')


    def getTokenizedSentences(self):
        """
        Purpose: Return a list of list of tokens (list of list of strings)
        """
        raise Exception('Must define selector for derived class')


    def getClassificationTuples(self):
        """
        Purpose: Return a list of (concept,line_number,start-ind,end-ind) tuples
        """
        raise Exception('Must define selector for derived class')


    def getLineIndices(self):
        """
        Purpose: Return a list of (start,end) char index pairs (one per line)
        """
        raise Exception('Must define selector for derived class')


    def setFileName(self):
        """
        Purpose: Set the note's text file base name (no extension)
                 (needed because SemEval format requires knowing filename)
        """
        raise Exception('Must define selector for derived class')


    def read_standard(self, txt, con=None):
        """
        Purpose: Every note must be able to read from standardized forat
        """
        raise Exception('Must define read_standard() for derived class')

