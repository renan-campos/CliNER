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


from utilities_for_notes import concept_cmp, SentenceTokenizer, WordTokenizer, lno_and_tokspan__to__char_span, lineno_and_tokspan
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

        print self.fileName

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

                    #print line

                    # Empty line
                    if line == '\n': continue

                    # Parse concept file line
                    fields = line.strip().split('|')
                    #print fields

                    cui     = fields[2]
                    span_inds = []

                    spans = fields[1]
                    spans = spans.split(',')
                    spans = [s.split('-') for s in spans]

                    for span in spans:
                        span = int(span[0]), int(span[1])
                        span_inds.append(span)

                    #for i in range(3,len(fields),2):
                    #    span = int(fields[i]), int(fields[i+1])
                    #    span_inds.append( span )

                    # Everything is a Disease_Disorder
                    concept = 'problem'

                    classifications.append( (concept, span_inds) )

            # Safe guard against concept file having duplicate entries
            classifications = sorted(classifications, cmp=concept_cmp)


            # Hack: Throw away noncontiguous spans that cross line numbers
            newClassifications = []
            for classification in classifications:
                concept,char_spans = classification

                # Each span (could be noncontiguous span)
                tok_spans = []
                first_lineno = None

                ignore = False
                for span in char_spans:
                    # character offset span --> lineno and list of token index spans
                    lineno,tokspan = lineno_and_tokspan(self.line_inds, self.data, self.text, span)
                    tok_spans.append(tokspan)

                    # Ensure all noncontig spans are together on one line
                    if first_lineno == None: first_lineno = lineno

                    # Throw away noncontig spans that cross lines 
                    if lineno != first_lineno:
                        ignore = True

                if not ignore:
                    newClassifications.append(classification)

            # Copy changes over
            classifications = newClassifications



            # Hack: Throw away subsumed spans
            # ex. "left and right atrial dilitation" from 02136-017465.text
            classifs = reduce(lambda a,b: a+b,map(lambda t:t[1],classifications))
            classifs = list(set(classifs))
            classifs = sorted(classifs, key=lambda s:s[0])
            #print classifs

            from utilities_for_notes import span_relationship

            newClassifications = []
            for c in classifications:

                ignore = False
                for span in c[1]:
                    #print '\t', span
                    
                    # Slow!
                    # Determine if any part of span is subsumed by other span
                    for cand in classifs:
                        # Don't let identity spans mess up comparison
                        if span == cand: continue

                        # Is current span subsumed?
                        rel = span_relationship(span,cand)
                        if rel == 'subsumes':
                            #print 'SUBSUMED!'
                            ignore = True

                # Only add if no spans are subsumed by others
                if not ignore:
                    newClassifications.append(c)

            #for c in newClassifications: print c
            self.classifications = newClassifications
    
            #for c in newClassifications:
            #    print c
            #exit()

            # Concept file does not guarantee ordering by line number
            #self.classifications = sorted(classifications, cmp=concept_cmp)




    def write(self, labels):

        # Case: User DOES provide predicted annotations (classification tuples)
        if labels != None:
            # Translate token-level annotations to character offsets
            classifications = []
            for classification in labels:
                # Data needed to recover original character offsets
                inds = self.line_inds
                data = self.data
                text = self.text
                
                # Unpack classification span
                concept  = classification[0]
                lno      = classification[1] - 1
                tokspans = classification[2]

                # Get character offset span                
                spans = []
                for tokspan in tokspans:
                    span = lno_and_tokspan__to__char_span(inds,data,text,
                                                                 lno,tokspan)
                    spans.append(span)
                classifications.append( (concept,spans) )

        elif self.classifications != None:
            classifications = self.classifications
        else:
            raise Exception('Cannot write concept file: must specify labels')


        # Assertion: 'classifications' is a list of (concept,char-span) tups


        # Build output string
        retStr = ''

        # system only covers semeval task 1.
        defaultDisorderSlots = '|no|null|patient|null|no|null|unmarked|null|unmarked|null|false|null|false|null|NULL|null'

        # For each classification, format to semeval style
        for concept,span_inds in classifications:

            spansAsStr = ",".join([str(span[0]) + '-' + str(span[1]) for span in span_inds])

            outputLine = "{0}|{1}|{2}".format(self.fileName, spansAsStr, 'CUI-less')

            outputLine += defaultDisorderSlots
            #retStr += self.fileName + '||%s||CUI-less' % concept
            #for span in span_inds:
            #    retStr += '||' + str(span[0]) + "||" +  str(span[1])
            retStr += (outputLine + '\n')

        return retStr
 
