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
        print "semeval note read called"

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
            #print sents[58]


            # Tokenize each sentence into words (and save line number indices)
            toks = []
            gold = []          # Actual lines
            
            i = 0
            for s in sents:
                i += 1
           
                gold.append(s)

                b = False
                if b: print "\nsentence:-------------------------------"
                if b: print '<s>' + s + '</s>'

                # Store data
                toks = self.word_tokenizer.tokenize(s)

                if b: print "\ntokenized sentence:----------------------------"
                if b: print toks

                self.data.append(toks)

                # Keep track of which indices each line has
                end = start + len(s)

                if b: print "\nindices:---------------------------------------"
                if b: print (start, end)

                if b: print "\nusing index on entire txt----------------------"
                if b: print '<s>' + text[start:end] + '</s>'

                # EQUAL?
                assert( text[start:end] == s ), 'data and text must agree'

                self.line_inds.append( (start,end) )
                start = end

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
                    concept = fields[1]
                    cui     = fields[2]
                    span_inds = []
                    for i in range(3,len(fields),2):
                        span = int(fields[i]), int(fields[i+1])
                        span_inds.append( span )

                    # Everything is a Disease_Disorder
                    concept = 'problem'

                    classifications.append( (concept, span_inds) )

            # Safe guard against concept file having duplicate entries
            #classifications = list(set(classifications))
            classifications = sorted(classifications, cmp=concept_cmp)

            '''
            # TODO - Atomize spans
            # Atomize classification spans
            # ex. "left and right atrial dilitation" from 02136-017465.text
            classifs = reduce(lambda a,b: a+b,map(lambda t:t[1],classifications))
            classifs = list(set(classifs))
            classifs = sorted(classifs, key=lambda s:s[0])
            print classifs

            from utilities_for_notes import span_stuff
            span_stuff(classifs)

            # Goal: Split overlaps
            #print self.text[6111:6134], ' -> <s>'+self.text[6111:6116]+'</s> <s>'+self.text[6117:6134]+'</s>'
            #print
            #print self.text[6117:6134]

            #print
            exit()
            '''

            # Hack: Throw away subsumed spans
            # ex. "left and right atrial dilitation" from 02136-017465.text
            classifs = reduce(lambda a,b: a+b,map(lambda t:t[1],classifications))
            classifs = list(set(classifs))
            classifs = sorted(classifs, key=lambda s:s[0])
            #print classifs

            from utilities_for_notes import span_relationship

            newClassifications = []
            for c in classifications:

                for span in c[1]:
                    #print span
                    
                    # Slow!
                    # Determine if any part of span is subsumed by other span
                    ignore = False
                    for cand in classifs:
                        # Don't let identity spans mess up comparison
                        if span == cand: continue

                        # Is current span subsumed?
                        rel = span_relationship(span,cand)
                        if rel == 'subsumes':
                            ignore = True

                # Only add if no spans are subsumed by others
                if not ignore:
                    newClassifications.append(c)

            #for c in newClassifications: print c
            self.classifications = newClassifications
    

            # Concept file does not guarantee ordering by line number
            #self.classifications = sorted(classifications, cmp=concept_cmp)




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
                concept  = classification[0]
                lno      = classification[1] - 1
                tokspans = classification[2]

                # Get character offset span                
                spans = []
                for tokspan in tokspans:
                    span = lno_and_tokspan__to__char_span(inds,data,text,lno,tokspan)
                    spans.append(span)
                classifications.append( (concept,spans) )

        elif self.classifications != None:
            classifications = self.classifications
        else:
            raise Exception('Cannot write concept file: must specify labels')

        # return value
        retStr = ''

        for concept,span_inds in classifications:
            retStr += self.fileName + '||%s||CUI-less' % concept
            for span in span_inds:
                retStr += '||' + str(span[0]) + "||" +  str(span[1])
            #retStr += '||' + str(span_inds[0]) + "||" +  str(span_inds[1])
            retStr += '\n'

        return retStr
 
