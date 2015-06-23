from __future__ import with_statement

######################################################################
#  CliNER - note.py                                                  #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Internal representation of data for CliNER.              #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Nov. 6, 2014'



import re
import os.path

from utilities_for_notes import lineno_and_tokspan


# Master Class
class Note:


    # Memoize results from static method calls
    supported_formats = []
    dict_of_format_to_extensions = []


    # Constructor
    def __init__(self, format):

        '''
        Note::__init__()

        Purpose: Instantiate an object to interface with scripts

        @param format. A string to indicate which format (e.g. "i2b2")

        >>> n = Note()
        Traceback (most recent call last):
         ...
        TypeError: __init__() takes exactly 2 arguments (1 given)

        >>> n = Note('not_a_valid_format')
        Traceback (most recent call last):
         ...
        Exception: Cannot create Note object for format not_a_valid_format

        >>> n = Note('i2b2')
        >>> n = Note('xml')
        >>> n = Note('semeval')
        '''

        # Error-check input
        if format not in Note.supportedFormats():
            raise Exception('Cannot create Note object for format %s' % format)

        # Instantiate the given format derived class
        cmd = 'from note_%s import Note_%s as DerivedNote' % (format,format)
        exec(cmd)
        self.derived_note = DerivedNote()

        # Helpful for debugging
        self.format = format

        # Memoizations of selectors
        self.data            = []
        self.concepts        = []
        self.iob_labels      = []
        self.text_chunks     = []



    @staticmethod
    def supportedFormats():

        '''
        Note::supportedFormats()

        Purpose: returns a list of data formats supported by CliNER

        >>> sorted(Note.supportedFormats())
        ['i2b2', 'semeval', 'xml']
        '''

        # Memoized?
        if Note.supported_formats: return Note.supported_formats

        # Note files
        cands = os.listdir(os.path.join(os.getenv('CLINER_DIR'),'cliner', 'notes'))
        notes = filter(lambda f:f.startswith('note_'), cands)
        notes = filter(lambda f:  f.endswith('.py'  ), notes)

        # Extract format name from all files like 'note_i2b2.py'
        formats = []
        for filename in notes:
            f = re.search('note_(.*)\\.py', filename).groups(1)[0]
            formats.append(f)

        return formats


    @staticmethod
    def supportedFormatExtensions():
        '''
        Note::supportedFormatExtensions()

        Purpose: returns a list of data format extensions supported by CliNER

        >>> sorted(Note.supportedFormatExtensions())
        ['con', 'pipe', 'xml']
        '''
        return Note.dictOfFormatToExtensions().values()



    @staticmethod
    def dictOfFormatToExtensions():
        '''
        Note::dictOfFormatToExtensions()

        Purpose: Create a mapping between CliNER formats and their file extensions

        >>> sorted( Note.dictOfFormatToExtensions().items() )
        [('i2b2', 'con'), ('semeval', 'pipe'), ('xml', 'xml')]
        '''

        # Memoized?
        if Note.dict_of_format_to_extensions:
            return Note.dict_of_format_to_extensions

        # Get each format's extension
        extensions = {}
        for format in Note.supportedFormats():
            # Import next note format
            cmd1 = 'from note_%s import Note_%s' % (format,format)
            exec(cmd1)

            # Get extension for note
            cmd2 = 'extensions[format] = Note_%s().getExtension()' % format
            exec(cmd2)

        Note.dict_of_format_to_extensions = extensions
        return extensions



    ##################################################################
    ####          Pass right on to derived format note            ####
    ####     (does not change as new formats are introduced)      ####
    ##################################################################

    def getExtension(self):
        '''
        Note::dictOfFormatToExtensions()

        Purpose: returns the filename extension for a given data format

        >>> n = Note('i2b2')
        >>> n.getExtension()
        'con'

        >>> n = Note('xml')
        >>> n.getExtension()
        'xml'

        >>> n = Note('semeval')
        >>> n.getExtension()
        'pipe'

        '''
        return self.derived_note.getExtension()


    def read(self, txt_file, con_file=None):
        """
        Note::read()

        Purpose: Call derived object's reader

        >>> n = Note('i2b2')
        >>> n.read()
        Traceback (most recent call last):
         ...
        TypeError: read() takes at least 2 arguments (1 given)

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n2 = Note('i2b2')
        >>> n2.read(txt_file, con_file)

        #>>> txt_file = 'data/multi.txt'
        #>>> con_file = 'data/multi.xml'
        #>>> n2 = Note('xml')
        #>>> n2.read(txt_file, con_file)

        #>>> txt_file = 'data/multi.txt'
        #>>> con_file = 'data/multi.pipe'
        #>>> n2 = Note('semeval')
        #>>> n2.read(txt_file, con_file)
        """
        retVal = self.derived_note.read(txt_file, con_file)
        self.getIOBLabels()
        return retVal


    def write(self, con_file=None):
        """
        Note::wrire()

        Purpose: Call derived object's writer

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n1 = Note('i2b2')
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
        return self.derived_note.write(con_file)


    def getTokenizedSentences(self):
        """
        Note::getTokenizedSentences()

        Purpose: Return list of list of tokens from text file.

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note('i2b2')
        >>> n.read(txt_file, con_file)
        >>> n.getTokenizedSentences()
        [['Title', ':'], ['Casey', 'at', 'the', 'Bat'], ['The', 'outlook', "wasn't", 'brilliant', 'for', 'the', 'Mudville', 'Nine', 'that', 'day', ';'], ['The', 'score', 'stood', 'four', 'to', 'two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']]
        """
        if not self.data:
            self.data = self.derived_note.getTokenizedSentences()
        return self.data


    def read_standard(self, txt, con=None):
        """
        Purpose: Every note must be able to read from standard forat

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file      = os.path.join(base_dir, 'data/multi.txt'     )
        >>> standard_file = os.path.join(base_dir, 'data/multi.standard')
        >>> n = Note('i2b2')
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
        >>> os.close(os_handle)
        """
        self.derived_note.read_standard(txt,con)
        self.getIOBLabels()



    ##################################################################
    ####                     Internal Logic                       ####
    ####     (does not change as new formats are introduced)      ####
    ##################################################################


    def getConceptLabels(self):
        """
        Note::getConceptLabels()

        Purpose: return a list of concept labels for second pass training

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note('i2b2')
        >>> n.read(txt_file, con_file)
        >>> n.getConceptLabels()
        ['treatment', 'problem']
        """
        classifications = self.derived_note.getClassificationTuples()
        return [  c[0]  for  c  in  classifications  ]


    def getIOBLabels(self):
        """
        Note::getIOBLabels()

        Purpose: return a list of list of IOB labels

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note('i2b2')
        >>> n.read(txt_file, con_file)
        >>> n.getIOBLabels()
        [['O', 'O'], ['B', 'I', 'I', 'I'], ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'], ['B', 'I', 'I', 'I', 'I', 'I', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']]
        """

        # Only comput if not already memoized
        if self.iob_labels: return self.iob_labels

        # Build list of proper dimensions (1:1 with self.data)
        self.getTokenizedSentences()
        iobs = [ ['O' for tok in sent] for sent in self.data ]

        line_inds = self.derived_note.getLineIndices()
        data = self.derived_note.data
        text = self.derived_note.text

        # Add 'B's and 'I's from concept spans
        for classification in self.derived_note.getClassificationTuples():
            concept,char_spans = classification

            # Each span (could be noncontiguous span)
            for span in char_spans:
                lineno,tokspan = lineno_and_tokspan(line_inds, data, text, span)
                start,end = tokspan

                # Update concept tokens to 'B's and 'I's
                iobs[lineno][start] = 'B'
                for i in range(start+1,end+1):
                    iobs[lineno][i] = 'I'

        # Memoize for next call
        self.iob_labels = iobs
        return iobs



    def setIOBLabels(self, iobs):
        """
        Note::setIOBLabels()

        Purpose: Set the IOB labels for the derived note

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> n = Note('i2b2')
        >>> n.read(txt_file)
        >>> iobs = [['O', 'O'], ['B', 'I', 'I', 'I'], ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'], ['B', 'I', 'I', 'I', 'I', 'I', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']]
        >>> n.setIOBLabels(iobs)
        >>> n.getIOBLabels() == iobs
        True
        """
        # Must be proper form
        for iob in iobs:
            for label in iob:
                assert (label == 'O') or (label == 'B') or (label == 'I'),  \
                       "All labels must be I, O, or B. Given: " + label

        self.iob_labels = iobs



    def getChunkedText(self):
        """
        Note::getChunkedText()

        Purpose: List of list of tokens, except combine all 'I's into 'B' chunks

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note('i2b2')
        >>> n.read(txt_file, con_file)
        >>> n.getChunkedText()
        [['Title', ':'], ['Casey at the Bat'], ['The', 'outlook', "wasn't", 'brilliant', 'for', 'the', 'Mudville', 'Nine', 'that', 'day', ';'], ['The score stood four to two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']]
        """

        # Memoized?
        if self.text_chunks: return self.text_chunks()

        # Line-by-line chunking
        text = self.getTokenizedSentences()
        for sent,iobs in zip(text,self.iob_labels):

            # One line of chunked phrases
            line = []

            # Chunk phrase (or single word if 'O' iob tag)
            phrase = ''

            # Word-by-word grouping
            for word,iob in zip(sent,iobs):

                if iob == 'O':
                    if phrase: line.append(phrase)
                    phrase = word

                if iob == 'B':
                    if phrase: line.append(phrase)
                    phrase = word

                if iob == 'I':
                    phrase += ' ' + word

            # Add last phrase
            if phrase: line.append(phrase)

            # Add line from file
            self.text_chunks.append(line)

        return self.text_chunks



    def getConceptIndices(self):

        '''
        Note::getConceptIndices()

        Purpose: Get parallel-to-tokens lines list of the chunk indices

        TODO: Get example that has two concepts one same line

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note('i2b2')
        >>> n.read(txt_file, con_file)
        >>> n.getConceptIndices()
        [[], [0], [], [0]]
        '''

        # Return value
        inds_list = []

        # Line-by-line chunking
        for iobs in self.iob_labels:

            # One line of chunked phrases
            line = []
            seen_chunks = 0

            # Word-by-word grouping
            for iob in iobs:

                if iob == 'O':
                    seen_chunks += 1

                if iob == 'B':
                    line.append(seen_chunks)
                    seen_chunks += 1

            # Add line from file
            inds_list.append(line)


        return inds_list



    def write_standard(self, labels=None):
        """
        Note::write_standard()

        Purpose: Every note must be able to read from standardized format

        @param  labels. A list of classifications
        @return         A string of starndardized formatted data

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note('i2b2')
        >>> n.read(txt_file, con_file)

        >>> import tempfile

        >>> out = n.write_standard()

        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> f = open(out_file, 'w')
        >>> print >>f, out
        >>> f.close()

        >>> import filecmp
        >>> standard_file = os.path.join(base_dir, 'data/multi.standard')
        >>> filecmp.cmp(standard_file, out_file)
        True
        >>> os.close(os_handle)


        >>> labels = [  ( 'treatment', [(8, 24)] ) ,  ( 'problem', [(87, 114)] )  ]
        >>> n2 = Note('i2b2')
        >>> n2.read(txt_file)
        >>> out = n2.write_standard(labels)

        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> f = open(out_file, 'w')
        >>> print >>f, out
        >>> f.close()

        >>> import filecmp
        >>> standard_file = os.path.join(base_dir, 'data/multi.standard')
        >>> filecmp.cmp(standard_file, out_file)
        True
        >>> os.close(os_handle)
        """

        # Standard will have:
        # 1. concept type
        # 2. concept span inds in character offsets

        # return value
        retStr = ''

        # Get data
        if labels != None:
            classifications = labels
        else:
            classifications = self.derived_note.getClassificationTuples()

        # Output classifications into standardized format
        for concept,span_inds in classifications:
            retStr += concept
            for span in span_inds:
                retStr += '||%d||%d' % span
            retStr += '\n'

        return retStr.strip('\n')




    ##################################################################
    ####         Only used during developmnt and testing          ####
    ##################################################################


    def conlist(self):
        """
        Note::conlist()

        Purpose: Label for each token (Useful during evaluation)

        >>> import os
        >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests')
        >>> txt_file = os.path.join(base_dir, 'data/multi.txt')
        >>> con_file = os.path.join(base_dir, 'data/multi.con')

        >>> n = Note('i2b2')
        >>> n.read(txt_file, con_file)
        >>> n.conlist()
        [['none', 'none'], ['treatment', 'treatment', 'treatment', 'treatment'], ['none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none'], ['problem', 'problem', 'problem', 'problem', 'problem', 'problem', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none']]
        """

        # Cached for later calls
        if self.concepts: return self.concepts

        # For each word, store a corresponding concept label
        # Initially, all labels will be stored as 'none'
        for line in self.data:
            tmp = []
            for word in line:
                tmp.append('none')
            self.concepts.append(tmp)

        # Use the classifications to correct all mislabled 'none's
        for classification in self.derived_note.getClassificationTuples():
            concept    = classification[0]
            char_spans = classification[1]

            # Assumption - assumes no clustering third pass
            line_inds = self.derived_note.getLineIndices()
            data      = self.derived_note.getTokenizedSentences()
            text      = self.derived_note.getText()
            for span in char_spans:
                lineno,tokspan = lineno_and_tokspan(line_inds, data, text, span)
                start,end = tokspan

            self.concepts[lineno][start] = concept
            for i in range(start, end):
                self.concepts[lineno][i+1] = concept

        return self.concepts




# Concept labels
concept_labels = {
    "none":0,
    "treatment":1,
    "problem":2,
    "test":3
}
reverse_concept_labels = {v:k for k, v in concept_labels.items()}


# IOB labels
IOB_labels = {
    'O':0,
    'B':1,
    'I':2
}
reverse_IOB_labels = {v:k for k,v in IOB_labels.items()}

