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

        # Internal representation natural for semeval format
        self.text = ''
        self.data            = []  # list of list of tokens
        self.line_inds = []
        self.classifications = []
        self.filename = 'no-file'


    def getExtension(self):
        return 'pipe'


    def getText(self):
        '''
        Note_semeval::getText()

        Purpose: Return the content of the text file

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.pipe')

        >>> n = Note_semeval()
        >>> n.read(txt_file, con_file)
        >>> out = n.getText()

        >>> import tempfile

        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> f = open(out_file, 'w')
        >>> print >>f, out
        >>> f.close()

        >>> import filecmp
        >>> filecmp.cmp(txt_file, out_file)
        True
        >>> import os
        >>> os.close(os_handle)
        '''
        return self.text


    def getTokenizedSentences(self):
        '''
        Note_semeval::getTokenizedSentences()

        Purpose: Get tokenized sentences from file

        Note: Could need to be updated if switching tokenizer

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.pipe')

        >>> n = Note_semeval()
        >>> n.read(txt_file, con_file)
        >>> n.getTokenizedSentences()
        [['Title', ':'], ['Casey', 'at', 'the', 'Bat'], ['The', 'outlook', "wasn't", 'brilliant', 'for', 'the', 'Mudville', 'Nine', 'that', 'day', ';'], ['The', 'score', 'stood', 'four', 'to', 'two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']]
        '''
        return self.data


    def getClassificationTuples(self):
        '''
        Note_semeval::getClassificationTuples()

        Purpose: Get the records that specify concept spans

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.pipe')

        >>> n = Note_semeval()
        >>> n.read(txt_file, con_file)
        >>> n.getClassificationTuples()
        [('problem', [(8, 24)]), ('problem', [(87, 114)])]
        '''
        return self.classifications


    def getLineIndices(self):
        '''
        Note_semeval::getLineIndices()

        Purpose: Get the list of (start,end) indices of line breaks in the text file.

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.pipe')

        >>> n = Note_semeval()
        >>> n.read(txt_file, con_file)
        >>> n.getLineIndices()
        [(0, 7), (8, 24), (25, 86), (87, 151)]
        '''
        return self.line_inds



    def read_standard(self, txt, con=None):
        """
        Purpose: Every note must be able to read from standard forat

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file      = os.path.join(base_dir, 'data/multi.txt'     )
        >>> standard_file = os.path.join(base_dir, 'data/multi.standard')

        >>> n = Note_semeval()
        >>> n.read_standard(txt_file, standard_file)

        >>> import tempfile

        >>> out = n.write()
        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> f = open(out_file, 'w')
        >>> f.write(out)
        >>> f.close()

        >>> import filecmp
        >>> con_file = os.path.join(base_dir, 'data/multi.pipe')
        >>> filecmp.cmp(con_file, out_file)
        True
        >>> import os
        >>> os.close(os_handle)
        """

        # Filename
        self.filename = os.path.split(txt)[1]

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
        """
        Note_semeval::read()

        @param txt. A file path for the tokenized medical record
        @param con. A file path for the semeval annotated concepts for txt

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/empty.txt')
        >>> con_file = os.path.join(base_dir, 'data/empty.pipe')

        >>> n2 = Note_semeval()
        >>> n2.read(txt_file, con_file)
        >>> n2.getText()
        ''
        >>> n2.getClassificationTuples()
        []
        >>> n2.getLineIndices()
        []

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/single.txt')
        >>> con_file = os.path.join(base_dir, 'data/single.pipe')

        >>> n4 = Note_semeval()
        >>> n4.read(txt_file, con_file)
        >>> n4.getText()
        'The score stood four to two , with but one inning more to play ,'
        >>> n4.getClassificationTuples()
        [('problem', [(0, 27)])]
        >>> n4.getLineIndices()
        [(0, 64)]

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.pipe')

        >>> n4 = Note_semeval()
        >>> n4.read(txt_file, con_file)
        >>> n4.getClassificationTuples()
        [('problem', [(8, 24)]), ('problem', [(87, 114)])]
        """

        # Filename
        self.filename = os.path.split(txt)[1]

        start = 0
        end = 0
        with open(txt) as f:

            # Get entire file
            text = f.read().strip()
            #print "TEXT:------------------"
            #print '<%s>' % text

            self.text = text

            # Sentence splitter
            sents = self.sent_tokenizer.tokenize(txt)
            sents = [ s.strip() for s in sents ]

            #print "SENTS:-----------------------------"
            #print sents

            # Tokenize each sentence into words (and save line number indices)
            toks = []
            gold = []          # Actual lines
            
            for s in sents:
           
                gold.append(s)

                #print "sentence:-------------------------------"
                #print s

                # Store data
                toks = self.word_tokenizer.tokenize(s)

                #print "tokenized sentence:---------------------------------"
                #print toks

                self.data.append(toks)

                # Keep track of which indices each line has
                end = start + len(s)

                #print "indices:--------------------------------------------"
                #print (start, end)

                #print "using index on entire txt----------------------------"
                #print text[start:end]

                #print "EQUAL?"
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




    def write(self, labels=None):

        """
        Note_semeval::write()

        Purpose: Return the given concept label predictions in semeval format

        @param  labels. A list of classifications
        @return         A string of semeval-concept-file-formatted data

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.pipe')

        >>> n1 = Note_semeval()
        >>> n1.read(txt_file, con_file)

        >>> import tempfile

        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')

        >>> out = n1.write()
        >>> f = open(out_file, 'w')
        >>> f.write(out)
        >>> f.close()

        >>> import filecmp
        >>> filecmp.cmp(con_file, out_file)
        True
        >>> import os
        >>> os.close(os_handle)
        """

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

        # SemEval expects that all labels are "Disease_Disorder"
        elif self.classifications != None:
            classifications = [('Disease_Disorder',i) for c,i in self.classifications]
        else:
            raise Exception('Cannot write concept file: must specify labels')

        # Build output string
        retStr = ''
        for concept,span_inds in classifications:
            retStr += self.filename + '||%s||CUI-less' % concept
            for span in span_inds:
                retStr += '||' + str(span[0]) + "||" +  str(span[1])
            retStr += '\n'

        return retStr
 
