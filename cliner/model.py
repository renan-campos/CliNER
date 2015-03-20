from __future__ import with_statement

import os
import cPickle as pickle
import helper
import sys

from sklearn.feature_extraction  import DictVectorizer

from machine_learning import sci
from machine_learning import crf
from features_dir import features, utilities

from notes.note import concept_labels, reverse_concept_labels
from notes.note import     IOB_labels,     reverse_IOB_labels
from tools      import flatten, save_list_structure, reconstruct_list

import globals_cliner



class Model:

    @staticmethod
    def load(filename='awesome.model'):
        with open(filename, 'rb') as model:
            model = pickle.load(model)
        model.filename = filename
        return model


    def __init__(self, is_crf=True):

        # Use python-crfsuite
        self._crf_enabled = is_crf

        # DictVectorizers
        self._first_prose_vec    = None
        self._first_nonprose_vec = None
        self._second_vec         = None

        # Classifiers
        self._first_prose_clf    = None
        self._first_nonprose_clf = None
        self._second_clf         = None




    def train(self, notes, do_grid=False):

        """
        Model::train()

        Purpose: Train a ML model on annotated data

        @param notes. A list of Note objects (containing text and annotations)
        @return       None
        """

        # Extract formatted data
        tokenized_sentences, iob_labels =  first_pass_data_and_labels(notes)
        chunks, indices    , con_labels = second_pass_data_and_labels(notes)

        # Learn first and second pass classifiers
        self.__first_train(tokenized_sentences , iob_labels, do_grid)
        self.__second_train(chunks, indices    , con_labels, do_grid)



    def predict(self, note):

        """
        Model::predict

        Purpose: Predict concept annotations for a given note

        @param note. A Note object (containing text and annotations)
        @return      <list> of Classification objects

        >>> ...
        """
        #FIXME: Create DUMMY feature extractor to test selectors


        # Extract formatted data for first pass
        tokenized_sentences =  first_pass_data(note)


        if globals_cliner.verbosity > 0:
            print 'first pass'


        # Predict IOB labels
        iobs = self.__first_predict(tokenized_sentences)
        note.setIOBLabels(iobs)


        if globals_cliner.verbosity > 0:
            print 'second pass'


        # Extract formatted data for first pass
        chunked_sentences, inds =  second_pass_data(note)

        # Predict concept labels
        classifications = self.__second_predict(chunked_sentences, inds)

        return classifications



    ############################################################################
    ###           Mid-level reformats data and sends to lower level          ###
    ############################################################################


    def __first_train(self, tokenized_sentences, Y, do_grid=False):

        """
        Model::__first_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param tokenized_sentences. <list> of tokenized sentences
        @param Y.                   <list-of-lists> of IOB labels for words
        @param do_grid.             <boolean> whether to perform a grid search

        @return          None
        """

        if globals_cliner.verbosity > 0:
            print 'first pass'


        if globals_cliner.verbosity > 0:
            print '\textracting  features (pass one)'


        # Feature extractor
        feat_obj = features.FeatureWrapper(tokenized_sentences)

        # FIXME 0000b - separate the partition from the feature extraction
        #                 (includes removing feat_obj as argument)
        # FIXME 0005 - rename variables to be more informative
        # Parition into prose v. nonprose
        prose, nonprose, pchunks, nchunks = partition_prose(tokenized_sentences, Y, feat_obj)


        # Train classifiers for prose and nonprose
        pvec, pclf = self.__generic_train(   'prose',    prose, pchunks, do_grid)
        nvec, nclf = self.__generic_train('nonprose', nonprose, nchunks, do_grid)

        # Save vectorizers
        self._first_prose_vec    = pvec
        self._first_nonprose_vec = nvec

        # Save classifiers
        self._first_prose_clf    = pclf
        self._first_nonprose_clf = nclf




    def __second_train(self, chunked_data, inds_list, con_labels, do_grid=False):

        """
        Model::__second_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data      <list> of tokenized sentences after collapsing chunks
        @param inds_list <list-of-lists> of indices
                           - assertion: len(data) == len(inds_list)
                           - one line of 'inds_list' contains a list of indices
                               into the corresponding line for 'data'
        @param con_labels <list> of concept label strings
                           - assertion: there are sum(len(inds_list)) labels
                              AKA each index from inds_list maps to a label
        @param do_grid   <boolean> indicating whether to perform a grid search

        @return          None
        """

        if globals_cliner.verbosity > 0:
            print 'second pass'


        if globals_cliner.verbosity > 0:
            print '\textracting  features (pass two)'


        # Feature extractor
        feat_obj = features.FeatureWrapper()

        # Extract features
        text_features = extract_concept_features(chunked_data, inds_list, feat_obj)


        if globals_cliner.verbosity > 0:
            print '\tvectorizing features (pass two)'

        # Vectorize labels
        numeric_labels = [  concept_labels[y]  for  y  in  con_labels  ]

        # Vectorize features
        self._second_vec = DictVectorizer()
        vectorized_features = self._second_vec.fit_transform(text_features)


        if globals_cliner.verbosity > 0:
            print '\ttraining  classifier (pass two)'


        # Train the model
        self._second_clf = sci.train(vectorized_features,numeric_labels,do_grid)




    def __first_predict(self, data):

        """
        Model::__first_predict()

        Purpose: Predict IOB chunks on data

        @param data.  A list of split sentences    (1 sent = 1 line from file)
        @return       A list of list of IOB labels (1:1 mapping with data)
        """

        # Create object that is a wrapper for the features
        feat_obj = features.FeatureWrapper()

        if globals_cliner.verbosity > 0:
            print '\textracting  features (pass one)'


        # FIXME 0007 - Replace with functions to partition and extract feats
        # separate prose and nonprose data
        prose    = []
        nonprose = []
        plinenos = []
        nlinenos = []
        for i,line in enumerate(data):
            isProse,feats = feat_obj.extract_IOB_features(line)
            if isProse:
                prose.append(feats)
                plinenos.append(i)
            else:
                nonprose.append(feats)
                nlinenos.append(i)


        # Predict labels for IOB prose and nonprose text
        plist = self.__generic_predict(   'prose',    prose, self._first_prose_vec   , self._first_prose_clf   )
        nlist = self.__generic_predict('nonprose', nonprose, self._first_nonprose_vec, self._first_nonprose_clf)


        # Stitch prose and nonprose data back together
        # translate IOB labels into a readable format
        prose_iobs    = []
        nonprose_iobs = []
        iobs          = []
        num2iob = lambda l: reverse_IOB_labels[int(l)]
        for sentence in data:
            if utilities.prose_sentence(sentence):
                prose_iobs.append( plist.pop(0) )
                prose_iobs[-1] = map(num2iob, prose_iobs[-1])
                iobs.append( prose_iobs[-1] )
            else:
                nonprose_iobs.append( nlist.pop(0) )
                nonprose_iobs[-1] = map(num2iob, nonprose_iobs[-1])
                iobs.append( nonprose_iobs[-1] )

        # list of list of IOB labels
        return iobs




    def __second_predict(self, chunked_sentences, inds_list):

        # If first pass predicted no concepts, then skip
        # NOTE: Special case because SVM cannot have empty input
        if sum([ len(inds) for inds in inds_list ]) == 0:
            return []


        if globals_cliner.verbosity > 0:
            print '\textracting  features (pass two)'


        # Create object that is a wrapper for the features
        feat_obj = features.FeatureWrapper()

        # Extract features
        text_features = extract_concept_features(chunked_sentences, inds_list, feat_obj)


        if globals_cliner.verbosity > 0:
            print '\tvectorizing features (pass two)'


        # Vectorize features
        vectorized_features = self._second_vec.transform(text_features)


        if globals_cliner.verbosity > 0:
            print '\tpredicting    labels (pass two)'


        # Predict concept labels
        out = sci.predict(self._second_clf, vectorized_features)

        # Line-by-line processing
        o = list(out)
        classifications = []
        for lineno,inds in enumerate(inds_list):

            # Skip empty line
            if not inds: continue

            # For each concept
            for ind in inds:

                # Get next concept
                concept = reverse_concept_labels[o.pop(0)]

                # Get start position (ex. 7th word of line)
                start = 0
                for i in range(ind):
                    start += len( chunked_sentences[lineno][i].split() )

                # Length of chunk
                length = len(chunked_sentences[lineno][ind].split())

                # Classification token
                classifications.append( (concept,lineno+1,start,start+length-1) )

        # Return classifications
        return classifications



    ############################################################################
    ###               Lowest-level (interfaces to ML modules)                ###
    ############################################################################


    def __generic_train(self, p_or_n, text_features, iob_labels, do_grid=False):

        '''
        Model::__generic_train()

        Purpose: Train that works for both prose and nonprose

        @param p_or_n.        <string> either "prose" or "nonprose"
        @param text_features. <list-of-lists> of feature dictionaries
        @param iob_labels.    <list> of "I", "O", and "B" labels
        @param do_grid.       <boolean> indicating whether to perform grid search
        '''

        # Must have data to train on
        if len(text_features) == 0:
            raise Exception('Training must have %s training examples' % p_or_n)

        # Vectorize IOB labels
        Y_labels = [  IOB_labels[y]  for  y  in  iob_labels  ]

        # Save list structure to reconstruct after vectorization
        offsets = save_list_structure(text_features)


        if globals_cliner.verbosity > 0:
            print '\tvectorizing features (pass one) ' + p_or_n


        # Vectorize features
        dvect = DictVectorizer()
        X_feats = dvect.fit_transform( flatten(text_features) )

        # CRF needs reconstructed lists
        if self._crf_enabled:
            X_feats  = reconstruct_list( list(X_feats) , offsets)
            Y_labels = reconstruct_list(      Y_labels , offsets)
            lib = crf
        else:
            lib = sci


        if globals_cliner.verbosity > 0:
            print '\ttraining classifiers (pass one) ' + p_or_n


        # Train classifier
        clf  = lib.train(X_feats, Y_labels, do_grid)

        return dvect,clf



    def __generic_predict(self, p_or_n, text_features, dvect, clf,do_grid=False):

        '''
        Model::__generic_predict()

        Purpose: Train that works for both prose and nonprose

        @param p_or_n.        <string> either "prose" or "nonprose"
        @param text_features. <list-of-lists> of feature dictionaries
        @param dvect.         <DictVectorizer>
        @param clf.           scikit-learn classifier
        @param do_grid.       <boolean> indicating whether to perform grid search
        '''

        # If nothing to predict, skip actual prediction
        if len(text_features) == 0:
            print '\tnothing to predict (pass one) ' + p_or_n
            return []

        # Save list structure to reconstruct after vectorization
        offsets = save_list_structure(text_features)


        if globals_cliner.verbosity > 0:
            print '\tvectorizing features (pass one) ' + p_or_n


        # Vectorize features
        dvect = DictVectorizer()
        X_feats = dvect.fit_transform( flatten(text_features) )


        if globals_cliner.verbosity > 0:
            print '\tpredicting    labels (pass one) ' + p_or_n


        # CRF requires reconstruct lists
        if self._crf_enabled:
            X_feats  = reconstruct_list( list(X_feats) , offsets)
            lib = crf
        else:
            lib = sci

        # Predict IOB labels
        out = lib.predict(clf, X_feats)

        # Format labels from output
        predictions  = reconstruct_list( out, offsets)
        return predictions





def extract_concept_features(chunked_sentences, inds_list, feat_obj):
    ''' extract conept (2nd pass) features from textual data '''
    X = []
    for s,inds in zip(chunked_sentences, inds_list):
        X += feat_obj.concept_features(s, inds)
    return X




def first_pass_data_and_labels(notes):

    '''
    first_pass_data_and_labels()

    Purpose: Interface with notes object to get text data and labels

    @param notes. List of Note objects
    @return <tuple> whose elements are:
              0) list of tokenized sentences
              1) list of labels for tokenized sentences

    >>> import os
    >>> from notes.note import Note
    >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
    >>> txt = os.path.join(base_dir, 'single.txt')
    >>> con = os.path.join(base_dir, 'single.con')
    >>> note_tmp = Note('i2b2')
    >>> note_tmp.read(txt, con)
    >>> notes = [note_tmp]
    >>> first_pass_data_and_labels(notes)
    ([['The', 'score', 'stood', 'four', 'to', 'two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']], [['B', 'I', 'I', 'I', 'I', 'I', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']])
    '''

    # Get the data and annotations from the Note objects
    l_tokenized_sentences = [ note.getTokenizedSentences() for note in notes ]
    l_iob_labels          = [ note.getIOBLabels()          for note in notes ]

    tokenized_sentences = flatten(l_tokenized_sentences)
    iob_labels          = flatten(l_iob_labels         )

    return tokenized_sentences, iob_labels




def second_pass_data_and_labels(notes):

    '''
    second_pass_data_and_labels()

    Purpose: Interface with notes object to get text data and labels

    @param notes. List of Note objects
    @return <tuple> whose elements are:
              0) list of chunked sentences
              0) list of list-of-indices designating chunks
              1) list of labels for chunks

    >>> import os
    >>> from notes.note import Note
    >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
    >>> txt = os.path.join(base_dir, 'single.txt')
    >>> con = os.path.join(base_dir, 'single.con')
    >>> note_tmp = Note('i2b2')
    >>> note_tmp.read(txt, con)
    >>> notes = [note_tmp]
    >>> second_pass_data_and_labels(notes)
    ([['The score stood four to two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']], [[0]], ['problem'])
    '''

    # Get the data and annotations from the Note objects
    l_chunked_sentences  = [  note.getChunkedText()     for  note  in  notes  ]
    l_inds_list          = [  note.getConceptIndices()  for  note  in  notes  ]
    l_con_labels         = [  note.getConceptLabels()   for  note  in  notes  ]

    chunked_sentences = flatten(l_chunked_sentences)
    inds_list         = flatten(l_inds_list        )
    con_labels        = flatten(l_con_labels       )

    return chunked_sentences, inds_list, con_labels



def first_pass_data(note):

    '''
    first_pass_data()

    Purpose: Interface with notes object to get first pass data

    @param note. Note objects
    @return      <list> of tokenized sentences

    >>> import os
    >>> from notes.note import Note
    >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
    >>> txt = os.path.join(base_dir, 'single.txt')
    >>> note = Note('i2b2')
    >>> note.read(txt)
    >>> first_pass_data(note)
    [['The', 'score', 'stood', 'four', 'to', 'two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']]
    '''

    return note.getTokenizedSentences()



def second_pass_data(note):

    '''
    second_pass_data()

    Purpose: Interface with notes object to get second pass data

    @param notes. List of Note objects
    @return <tuple> whose elements are:
              0) list of chunked sentences
              0) list of list-of-indices designating chunks

    >>> import os
    >>> from notes.note import Note
    >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
    >>> txt = os.path.join(base_dir, 'single.txt')
    >>> note = Note('i2b2')
    >>> note.read(txt, con)
    >>> second_pass_data(note)
    ([['The score stood four to two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']], [[0]])
    '''

    # Get the data and annotations from the Note objects
    chunked_sentences = note.getChunkedText()
    inds              = note.getConceptIndices()

    return chunked_sentences, inds






def partition_prose(data, Y, feat_obj):

    '''
    partition_prose

    Purpose: Partition data (and corresponding labels) into prose and nonprose sections

    @param data. list of tokenized sentences
    @param Y.    list of corresponding labels for tokenized sentences
    @return <tuple> whose four elements are:
            0) foo
            1) bar
            2) baz
            3) quux

    >>> ...
    >>> data = ...
    >>> Y = ...
    >>> feat_obj = ... # eventually want to get rid of this argument
    >>> partition_prose(data, Y, feat_obj)
    ...
    '''

    # FIXME 0000a - separate the partition from the feature extraction

    prose    = []
    nonprose = []
    pchunks = []
    nchunks = []
    for line,labels in zip(data,Y):
        isProse,feats = feat_obj.extract_IOB_features(line)
        if isProse:
            prose.append(feats)
            pchunks += labels
        else:
            nonprose.append(feats)
            nchunks += labels

    return prose, nonprose, pchunks, nchunks

