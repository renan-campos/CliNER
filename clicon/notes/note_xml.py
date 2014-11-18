from __future__ import with_statement


######################################################################
#  CliNER - note_xml.py                                              #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Derived note object for reading xml formatted data.      #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Nov. 6, 2014'



import re
import string
from copy import copy
import nltk.data
import os.path


from abstract_note       import AbstractNote
from utilities_for_notes import classification_cmp, lineno_and_tokspan


class Note_xml(AbstractNote):

    def __init__(self):
        # Internal representation natural for i2b2 format
        self.data            = []  # list of list of tokens
        self.classifications = []  # list of concept tuples
        self.line_inds       = []  # list of (start,end) line character offsets


    def getExtension(self):
        return 'xml'


    def getText(self):
        return self.text


    def getTokenizedSentences(self):
        return self.data


    def setFileName(self, fname):
        pass # Not needed by Note_xml


    def getClassificationTuples(self):
        # return value
        retVal = []

        # Indices of each line
        line_inds = []
        start = 0
        end = 0
        for sent in self.data:
            for word in sent:
                end += len(word) + 1
            line_inds.append( (start,end-1) )
            start = end

        # Build list of standardized classification tuples
        for classification in self.classifications:
            concept,lineno,tok_start,tok_end = classification

            # character offset of beginning of line
            begin = line_inds[lineno-1][0]

            # Sweep through line to get character offsets from line start
            start = 0
            for word in self.data[lineno-1][:tok_start]:
                start += len(word) + 1

            # Length of concept span
            end = start
            for word in self.data[lineno-1][tok_start:tok_end+1]:
                end += len(word) + 1
            end -= 1

            #print begin
            #print begin+start, begin+end
            #print '~~' + self.text[begin+start:begin+end] + '~~'

            retVal.append( (concept,[(begin+start,begin+end)]) )

        return retVal



    def read(self, txt, con=None):

        """
        Note_xml::read()

        @param txt. A file path for the tokenized medical record
        @param con. A file path for the xml annotated concepts for txt
        """

        start = 0
        end = 0

        # Read in the medical text
        with open(txt) as f:
            for line in f:

                # Keep track of line's character offsets
                for word in line.split():
                    end += len(word) + 1
                self.line_inds.append( (start,end-1) )
                start = end

                # Strip away non-printable characters
                line = filter(lambda x: x in string.printable, line)

                # Add sentence to the data list
                self.data.append(line.split())


        # Read in the medical text
        if con:
            with open(con, 'r') as f:

                for lineno,line in enumerate(f.readlines()):

                    # Stored data for self.classifications
                    concept = 'N/A'
                    start_ind = -1
                    i = 0

                    for word in line.split():

                        # Search for xml tag
                        match = re.search('<(.*)>', word)
                        if match:

                            con = match.group(1)
                            
                            # begin tag
                            if con[0] != '/':
                                # store data 
                                concept = con
                                start_ind = i

                            # end tag
                            else:
                                # store data 
                                tup = (concept,lineno+1,start_ind,i-1)
                                self.classifications.append(tup)

                        # non-tag text
                        else:

                            # Next token
                            i += 1



    def write(self, labels=None):

        """
        Note_xml::write()
        
        Purpose: Write the concept predictions in xml format
        
        @param  labels. A list of predictions of labels for the given text.
        @return         A string for the xml-annotated file
        """


        # If given labels to write, use them. Default to self.classifications
        if labels != None:
            classifications = labels
        elif self.classifications:
            classifications = self.classifications
        else:
            raise Exception('Cannot write concept file: must specify labels')


        # Intermediate copy
        toks = copy(self.data)

        # Order classification tuples so they are accessed right to left
        # Assumption: sorted() is a stable sort
        tags = sorted(classifications, key=lambda x:x[2], reverse=True)
        tags = sorted(tags           , key=lambda x:x[1]              )

        #print toks
        #print ''
        #print ''

        # Insert each xml tag into its proper location
        for tag in tags:

            # Decode classification tuple
            con   = tag[0]
            line  = tag[1] - 1
            start = tag[2]
            end   = tag[3]

            #print tag
            #print 'line:   ', toks[line]
            #print 'phrase: ', toks[line][start:end+1]

            # Insert tags
            toks[line].insert(end+1, '</' + con + '>')
            toks[line].insert(start, '<'  + con + '>')

            #print 'line:   ', toks[line]
            #print ''

        # Stitch text back together
        toks = [  ' '.join(s)  for  s  in toks  ]
        output = '\n'.join(toks)

        return output



    def read_standard(self, txt, con=None):

        """
        Note_xml::read_standard()

        @param txt. A file path for the tokenized medical record
        @param con. A file path for the standardized annotated concepts for txt
        """

        start = 0
        end = 0

        with open(txt) as f:

            # Get entire file
            text = f.read()
            self.text = text

            # Split into lines
            self.data = map(lambda s: s.split(), text.split('\n'))

            # Tokenize each sentence into words (and save line number indices)
            toks = []
            gold = []          # Actual lines

            for sent in self.data:

                gold.append(sent)

                # Keep track of which indices each line has
                for word in sent:
                    end += len(word) + 1

                self.line_inds.append( (start,end-1) )
                start = end

                # Skip ahead to next non-whitespace
                while (start < len(text)) and text[start].isspace(): start += 1


        # If an accompanying concept file was specified, read it
        if con:
            classifications = []
            with open(con) as f:
                for line in f:

                    # Empty line
                    if line == '\n': continue

                    # Parse concept file line
                    fields = line.strip().split('||')
                    #print fields
                    concept = fields[0]
                    span_inds = []
                    for i in range(1,len(fields),2):
                        span = int(fields[i]), int(fields[i+1])
                        span_inds.append( span )

                    # FIXME - For now, treat non-contiguous spans as separate
                    for span in span_inds:
                        # Add the classification to the Note object
                        l,(start,end) = lineno_and_tokspan(self.line_inds, self.data, self.text, span)
                        #print 'span:   ', span
                        #print 'lineno: ', l
                        #print 'start:  ', start
                        #print 'end:    ', end
                        #print '\n'
                        classifications.append((concept,l+1,start,end))

            # Safe guard against concept file having duplicate entries
            classifications = list(set(classifications))

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications,cmp=classification_cmp)


