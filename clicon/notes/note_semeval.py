from __future__ import with_statement


######################################################################
#  CliNER - note_semeval.py                                          #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Derived note object for reading semeval formatted data.  #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Nov. 6, 2014'



import re
import string
from copy import copy
import os.path


from utilities_for_notes import concept_cmp, SentenceTokenizer, WordTokenizer, lno_and_tokspan__to__char_span
from abstract_note       import AbstractNote



class Note_semeval(AbstractNote):

    def __init__(self):
        # For parsing text file
        self.sent_tokenizer = SentenceTokenizer()
        self.word_tokenizer = WordTokenizer()

        # Internal representation natural for i2b2 format
        self.text = ''
        self.data            = []  # list of list of tokens
        self.line_inds = []
        self.classifications = []
        self.fileName = 'no-file'


    def getExtension(self):
        return 'pipe'


    def getText(self):
        return self.text


    def getTokenizedSentences(self):
        return self.data


    def getClassificationTuples(self):
        return self.classifications


    def getLineIndices(self):
        return self.line_inds


    def setFileName(self, fname):
        self.fileName = fname


    def read_standard(self, txt, con=None):

        start = 0
        end = 0

        with open(txt) as f:

            # Get entire file
            text = f.read()
            self.text = text

            # Sentence splitter
            sents = self.sent_tokenizer.tokenize(txt)

            # Tokenize each sentence into words (and save line number indices)
            toks = []
            gold = []          # Actual lines
            
            for s in sents:
                gold.append(s)

                # Store data
                toks = self.word_tokenizer.tokenize(s)
                self.data.append(toks)

                # Keep track of which indices each line has
                end = start + len(s)

                self.line_inds.append( (start,end) )
                start = end + 1

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

                    #print '\t', concept
                    #print '\t', span_inds

                    classifications.append( (concept, span_inds) )

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications, cmp=concept_cmp)




    def read(self, txt, con=None):            

        # Filename
        self.fileName = txt

        start = 0
        end = 0
        with open(txt) as f:

            # Get entire file
            text = f.read()
            #print "\nTEXT:------------------"
            #print text

            self.text = text

            # Sentence splitter
            sents = self.sent_tokenizer.tokenize(txt)

            #print "\nSENTS:-----------------------------"
            #print sents

            # Tokenize each sentence into words (and save line number indices)
            toks = []
            gold = []          # Actual lines
            
            for s in sents:
           
                gold.append(s)

                #print "\nsentence:-------------------------------"
                #print s

                #print s

                # Store data
                toks = self.word_tokenizer.tokenize(s)

                #print "\ntokenized sentence:---------------------------------"
                #print toks

                self.data.append(toks)

                # Keep track of which indices each line has
                end = start + len(s)

                #print "\nindices:--------------------------------------------"
                #print (start, end)

                #print "\nusing index on entire txt----------------------------"
                #print text[start:end]

                #print "\nEQUAL?"
                #print text[start:end] == s

                self.line_inds.append( (start,end) )
                start = end + 1

                # Skip ahead to next non-whitespace
                while (start < len(text)) and text[start].isspace(): start += 1

            '''
            for line,inds in zip(gold,self.line_inds):
                print '!!!' + line + '!!!'
                print '\t', 'xx'*10
                print inds
                print '\t', 'xx'*10
                print '!!!' + text[inds[0]: inds[1]] + '!!!'
                print '---'
                print '\n'
                print 'Xx' * 20
            '''

        #lno,span = lineno_and_tokspan((2329, 2351))
        #lno,span = lineno_and_tokspan((1327, 1344))
        #print self.data[lno][span[0]:span[1]+1]


        # If an accompanying concept file was specified, read it
        if con:
            offset_classifications = []
            classifications = []
            with open(con) as f:
                for line in f:

                    # Empty line
                    if line == '\n': continue

                    # Parse concept file line
                    fields = line.strip().split('||')
                    #print fields
                    concept = fields[1]
                    cui     = fields[2]
                    span_inds = []
                    for i in range(3,len(fields),2):
                        span = int(fields[i]), int(fields[i+1])
                        span_inds.append( span )

                    #print '\t', concept
                    #print '\t', span_inds

                    # Everything is a Disease_Disorder
                    concept = 'problem'

                    # FIXME - For now, treat non-contiguous spans as separate
                    for span in span_inds:
                        #l,(start,end) = lineno_and_tokspan(span)
                        # Add the classification to the Note object
                        offset_classifications.append((concept,span[0],span[1]))
                    classifications.append( (concept, span_inds) )

            # Safe guard against concept file having duplicate entries
            #classifications = list(set(classifications))

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications, cmp=concept_cmp)




    def write(self, labels):

        # If given labels to write, use them. Default to self.classifications
        if labels != None:
            # Translate token-level annotations to character offsets
            classifications = []
            for classification in labels:
                inds = self.line_inds
                data = self.data
                text = self.text
                
                # FIXME - Assumes that token-level does not have noncontig
                concept = classification[0]
                lno     = classification[1] - 1
                start   = classification[2]
                end     = classification[3]
                tokspan = start,end

                # Get character offset span                
                span = lno_and_tokspan__to__char_span(inds,data,text,lno,tokspan)
                classifications.append( (concept,span) )

        elif self.classifications != None:
            classifications = self.classifications
        else:
            raise Exception('Cannot write concept file: must specify labels')

        # return value
        retStr = ''

        for concept,span_inds in classifications:
            retStr += self.fileName + '||%s||CUI-less' % concept
            # ASSUME: no non-contig
            #for span in span_inds:
            #    retStr += '||' + str(span[0]) + "||" +  str(span[1])
            retStr += '||' + str(span_inds[0]) + "||" +  str(span_inds[1])
            retStr += '\n'

        return retStr
 
