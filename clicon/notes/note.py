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
import string
from copy import copy
import nltk.data
import os.path


from utilities_for_notes import lineno_and_tokspan


# Master Class
class Note:

    # Memoize results from static method calls
    supported_formats = []
    dict_of_format_to_extensions = []

    # Constructor
    def __init__(self, format):

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
        """ returns a list of data formats supported by CliNER """

        # Memoized?
        if Note.supported_formats: return Note.supported_formats

        # Note files
        cands = os.listdir(os.path.join(os.getenv('CLICON_DIR'),'clicon/notes'))
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
        return Note.dictOfFormatToExtensions().values()



    @staticmethod
    def dictOfFormatToExtensions():
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
        """ 
        Purpose: returns the filename extension for a given data format 
        """
        return self.derived_note.getExtension()

    def read(self, txt_file, con_file=None):
        """
        Purpose: Call derived object's reader
        """
        retVal = self.derived_note.read(txt_file, con_file)
        self.getIOBLabels()
        return retVal

    def write(self, con_file=None):
        """
        Purpose: Call derived object's writer
        """
        return self.derived_note.write(con_file)

    def getTokenizedSentences(self):
        """
        Purpose: Return list of list of tokens from text file.
        """
        if not self.data:
            self.data = self.derived_note.getTokenizedSentences()
        return self.data

    def setFileName(self, fname):
        """
        Purpose: Some formats (like semeval) need the filename as part of format
        """
        self.derived_note.setFileName(fname)

    def read_standard(self, txt, con=None):
        """
        Purpose: Every note must be able to read from standard forat
        """
        self.derived_note.read_standard(txt,con)
        self.getIOBLabels()



    ##################################################################
    ####                     Internal Logic                       ####
    ####     (does not change as new formats are introduced)      ####
    ##################################################################


    def getConceptLabels(self):
        """
        Purpose: return a list of concept labels for second pass training
        """
        classifications = self.derived_note.getClassificationTuples()
        return [  c[0]  for  c  in  classifications  ]


    def getIOBLabels(self):
        """
        Purpose: return a list of list of IOB labels
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
        Purpose: Set the IOB labels for the derived note
        """
        # Must be proper form
        for iob in iobs:
            for label in iob:
                assert (label == 'O') or (label == 'B') or (label == 'I'),  \
                       "All labels must be I, O, or B. Given: " + label

        self.iob_labels = iobs



    def getChunkedText(self):
        """
        Purpose: List of list of tokens, except combine all 'I's into 'B' chunks
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
        """

        # Standard will have:
        # 1. concept type
        # 2. concept span inds in character offsets

        # return value
        retStr = ''

        # Get data
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
        Useful during evaluation
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

