from __future__ import with_statement


######################################################################
#  CliNER - note_i2b2.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Derived note object for reading i2b2 formatted data.     #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Nov. 6, 2014'


import string

from abstract_note import AbstractNote
from utilities_for_notes import classification_cmp, lineno_and_tokspan


class Note_i2b2(AbstractNote):

    def __init__(self):
        # Internal representation natural for i2b2 format
        self.data            = []  # list of list of tokens
        self.classifications = []  # list of concept tuples
        self.line_inds       = []  # list of (start,end) indices for every line


    def getExtension(self):
        return 'con'


    def getText(self):
        '''
        Note_i2b2::getText()

        Purpose: 

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note_i2b2()
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
        Note_i2b2::getTokenizedSentences()

        Purpose: Get tokenized sentences from file

        Note: Could need to be updated if switching tokenizer

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note_i2b2()
        >>> n.read(txt_file, con_file)
        >>> n.getTokenizedSentences()
        [['Title', ':'], ['Casey', 'at', 'the', 'Bat'], ['The', 'outlook', "wasn't", 'brilliant', 'for', 'the', 'Mudville', 'Nine', 'that', 'day', ';'], ['The', 'score', 'stood', 'four', 'to', 'two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']]
        '''
        return map(lambda s: (' '.join(s)).split(), self.data)


    def getClassificationTuples(self):

        '''
        Note_i2b2::getClassificationTuples()

        Purpose: Get the records that specify concept spans

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note_i2b2()
        >>> n.read(txt_file, con_file)
        >>> n.getClassificationTuples()
        [('treatment', [(8, 24)]), ('problem', [(87, 114)])]
        '''

        # return value
        retVal = []

        # Build list of standardized classification tuples
        for classification in self.classifications:
            concept,lineno,tok_start,tok_end = classification

            # character offset of beginning of line
            begin = self.line_inds[lineno-1][0]

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


    def getLineIndices(self):
        '''
        Note_i2b2::getLineIndices()

        Purpose: Get the list of (start,end) indices of line breaks in the text file.

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note_i2b2()
        >>> n.read(txt_file, con_file)
        >>> n.getLineIndices()
        [(0, 7), (8, 24), (25, 86), (87, 151)]
        '''
        return self.line_inds


    def read_standard(self, txt, con=None):

        """
        Note_i2b2::read_standard()

        Purpose: Every note must be able to read from standard forat

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file      = os.path.join(base_dir, 'data/multi.txt'     )
        >>> standard_file = os.path.join(base_dir, 'data/multi.standard')

        >>> n = Note_i2b2()
        >>> n.read_standard(txt_file, standard_file)

        >>> import tempfile

        >>> out = n.write()
        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> f = open(out_file, 'w')
        >>> f.write(out)
        >>> f.close()

        >>> import filecmp
        >>> con_file = os.path.join(base_dir, 'data/multi.con')
        >>> filecmp.cmp(con_file, out_file)
        True
        >>> import os
        >>> os.close(os_handle)
        """

        start = 0
        end = 0

        with open(txt) as f:

            # Get entire file
            text = f.read().strip('\n')
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
                        l,(start,end) = lineno_and_tokspan(self.line_inds,
                                                           self.data,
                                                           self.text,
                                                           span)
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



    def read(self, txt, con=None):
        """
        Note_i2b2::read()

        @param txt. A file path for the tokenized medical record
        @param con. A file path for the i2b2 annotated concepts for txt

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/empty.txt')
        >>> con_file = os.path.join(base_dir, 'data/empty.con')

        >>> n2 = Note_i2b2()
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
        >>> con_file = os.path.join(base_dir, 'data/single.con')

        >>> n4 = Note_i2b2()
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
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n4 = Note_i2b2()
        >>> n4.read(txt_file, con_file)
        >>> n4.getClassificationTuples()
        [('treatment', [(8, 24)]), ('problem', [(87, 114)])]
        """

        # Character indices of each line
        start = 0
        end = 0

        # Read in the medical text
        with open(txt) as f:

            # Original text file
            self.text = f.read().strip('\n')

            if self.text:
                i = 0
                for line in self.text.split('\n'):
                    end += len(line) + 1
                    self.line_inds.append( (start,end-1) )
                    start = end

                    # Strip away non-printable characters
                    line = filter(lambda x: x in string.printable, line)

                    # Add sentence to the data list
                    self.data.append(line.split(' '))

        # TEST - is line_inds correct?
        #print self.line_inds
        #i = 0
        #for line,span in zip(self.data,self.line_inds):
        #    start,end = span
        #    print '<t>' + self.text[start:end] + '</t>'
        #    print '<l>' + ' '.join(line)       + '</l>'
        #    print
        #    i += 1
        #    if i == 13: exit()

        # If an accompanying concept file was specified, read it
        if con:
            classifications = []
            with open(con) as f:
                for line in f:

                    # Empty line
                    if line == '\n': continue

                    # concept
                    prefix, suffix = line.split('||')
                    text = prefix.split()
                    conc = suffix[3:-2]

                    start = text[-2].split(':')
                    end   = text[-1].split(':')

                    assert "concept spans one line", start[0] == end[0]

                    # lineno
                    l = int(start[0])

                    # starttok
                    # endtok
                    start = int(start[1])
                    end   = int(  end[1])

                    # Add the classification to the Note object
                    classifications.append( (conc,l,start,end) )

                    #print "txt:   ", txt
                    #print "l:     ", l
                    #print "start: ", start
                    #print "end:   ", end
                    #print "line:  ", self.data[l-1]

                    #print "\n" + "-" * 80

            # Safe guard against concept file having duplicate entries
            classifications = list(set(classifications))

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications,
                                          cmp=classification_cmp)


    def write(self, labels=None):

        """
        Note_i2b2::write()

        Purpose: Return the given concept label predictions in i2b2 format

        @param  labels. A list of classifications
        @return         A string of i2b2-concept-file-formatted data

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n1 = Note_i2b2()
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

        # Return value
        retStr = ''

        # List of list of words (line-by-line)
        tlist = self.data


        # If given labels to write, use them. Default to self.classifications
        if labels != None:
            classifications = labels
        elif self.classifications != None:
            classifications = self.classifications
        else:
            raise Exception('Cannot write concept file: must specify labels')


        # For each classification
        for classification in classifications:

            # Ensure 'none' classifications are skipped
            if classification[0] == 'none':
                raise('Classification label "none" should never happen')

            concept = classification[0]
            lineno  = classification[1]
            start   = classification[2]
            end     = classification[3]

            # A list of words (corresponding line from the text file)
            text = tlist[lineno-1]

            #print "\n" + "-" * 80
            #print "classification: ", classification
            #print "lineno:         ", lineno
            #print "start:          ", start
            #print "end             ", end
            #print "text:           ", text
            #print "text[start]:    ", text[start]
            #print "concept:        ", concept

            # The text string of words that has been classified
            datum = text[start]
            for j in range(start, end):
                datum += " " + text[j+1]

            # Line:TokenNumber of where the concept starts and ends
            idx1 = "%d:%d" % (lineno, start)
            idx2 = "%d:%d" % (lineno, end  )

            # Classification
            label = concept

            # Fixing issue involving i2b2 format (remove capitalization)
            lowercased = [w.lower() for w in datum.split()]
            datum = ' '.join(lowercased)

            # Print format
            retStr +=  "c=\"%s\" %s %s||t=\"%s\"\n" % (datum, idx1, idx2, label)

        # return formatted data
        return retStr

