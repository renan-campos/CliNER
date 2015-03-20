from __future__ import with_statement

import os
import cPickle as pickle
import helper
import sys

from sklearn.feature_extraction  import DictVectorizer

from machine_learning import sci
from machine_learning import crf
from features_dir import features, utilities

from notes.note import concept_labels, reverse_concept_labels, IOB_labels, reverse_IOB_labels




class Model:

    @staticmethod
    def load(filename='awesome.model'):
        with open(filename, 'rb') as model:
            model = pickle.load(model)
        model.filename = filename
        return model


    def __init__(self, is_crf=True):

        # Use python-crfsuite
        self.crf_enabled = is_crf

        # DictVectorizers
        self.first_prose_vec    = DictVectorizer()
        self.first_nonprose_vec = DictVectorizer()
        self.second_vec         = DictVectorizer()

        # Classifiers
        self.first_prose_clf    = None
        self.first_nonprose_clf = None
        self.second_clf         = None



    def train(self, notes, do_grid=False):

        """
        Model::train()

        Purpose: Train a ML model on annotated data

        @param notes. A list of Note objects (containing text and annotations)
        @return       None
        """


        ##############
        # First pass #
        ##############

        tokenized_sentences, iob_labels = first_pass_features_and_labels(notes)

        # Train classifier (side effect - saved as object's member variable)
        # TODO - Add verbosity levels for output
        print 'first pass'
        self.first_train(tokenized_sentences, iob_labels, do_grid)



        ###############
        # Second pass #
        ###############

        # FIXME - Do same abstraction method as done for first pass

        # Get the data and annotations from the Note objects
        chunks  = [  note.getChunkedText()     for  note  in  notes  ]
        indices = [  note.getConceptIndices()  for  note  in  notes  ]
        conlist = [  note.getConceptLabels()   for  note  in  notes  ]

        data2 = reduce( concat, chunks  )
        inds  = reduce( concat, indices )
        Y2    = reduce( concat, conlist )


        # Train classifier (side effect - saved as object's member variable)
        print 'second pass'
        self.second_train(data2, inds, Y2, do_grid)




    def first_train(self, data, Y, do_grid=False):

        """
        Model::first_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data      A list of split sentences    (1 sent = 1 line from file)
        @param Y         A list of list of IOB labels (1:1 mapping with data)
        @param do_grid   A boolean indicating whether to perform a grid search

        @return          None
        """

        print '\textracting  features (pass one)'


        # Create object that is a wrapper for the features
        feat_obj = features.FeatureWrapper(data)


        # FIXME 0000b - separate the partition from the feature extraction
        #                 (includes removing feat_obj as argument)
        # Parition into prose v. nonprose
        prose, nonprose, pchunks, nchunks = partition_prose(data, Y, feat_obj)


        # FIXME 0001 - make this into a function that is called twice
        # Classify both prose & nonprose
        flabels    = ['prose'             , 'nonprose'             ]
        fsets      = [prose               , nonprose               ]
        chunksets  = [pchunks             , nchunks                ]
        dvects     = [self.first_prose_vec, self.first_nonprose_vec]
        clfs       = [self.first_prose_clf, self.first_nonprose_clf]

        vectorizers = []
        classifiers = []

        for flabel,fset,chunks,dvect,clf in zip(flabels, fsets, chunksets, dvects, clfs):

            if len(fset) == 0:
                raise Exception('Training data must have %s training examples' % flabel)

            print '\tvectorizing features (pass one) ' + flabel

            # Vectorize IOB labels
            Y = [  IOB_labels[y]  for  y  in  chunks  ]

            # Save list structure to reconstruct after vectorization
            offsets = [ len(sublist) for sublist in fset ]
            for i in range(1, len(offsets)):
                offsets[i] += offsets[i-1]

            # Vectorize features
            flattened = [item for sublist in fset for item in sublist]
            X = dvect.fit_transform(flattened)
            vectorizers.append(dvect)


            print '\ttraining classifiers (pass one) ' + flabel

            # CRF needs reconstructed lists
            if self.crf_enabled:
                X = list(X)
                X = [ X[i:j] for i, j in zip([0] + offsets, offsets)]
                Y = [ Y[i:j] for i, j in zip([0] + offsets, offsets)]
                lib = crf
            else:
                lib = sci

            # Train classifiers
            clf  = lib.train(X, Y, do_grid)
            classifiers.append(clf)


        # Save vectorizers
        self.first_prose_vec    = vectorizers[0]
        self.first_nonprose_vec = vectorizers[1]

        # Save classifiers
        self.first_prose_clf    = classifiers[0]
        self.first_nonprose_clf = classifiers[1]




    # Model::second_train()
    #
    #
    def second_train(self, data, inds_list, Y, do_grid=False):

        """
        Model::second_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data      A list of list of strings.
                           - A string is a chunked phrase
                           - An inner list corresponds to one line from the file
        @param inds_list A list of list of integer indices
                           - assertion: len(data) == len(inds_list)
                           - one line of 'inds_list' contains a list of indices
                               into the corresponding line for 'data'
        @param Y         A list of concept labels
                           - assertion: there are sum(len(inds_list)) labels
                               AKA each index from inds_list maps to a label
        @param do_grid   A boolean indicating whether to perform a grid search

        @return          None
        """

        print '\textracting  features (pass two)'

        # Create object that is a wrapper for the features
        feat_o = features.FeatureWrapper()

        # Extract features
        X = [ feat_o.concept_features(s,inds) for s,inds in zip(data,inds_list) ]
        X = reduce(concat, X)


        print '\tvectorizing features (pass two)'

        # Vectorize labels
        Y = [  concept_labels[y]  for  y  in  Y  ]

        # Vectorize features
        X = self.second_vec.fit_transform(X)


        print '\ttraining  classifier (pass two)'


        # Train the model
        self.second_clf = sci.train(X, Y, do_grid)




    # Model::predict()
    #
    # @param note. A Note object that contains the data
    def predict(self, note):


        ##############
        # First pass #
        ##############


        print 'first pass'

        # FIXME 0003 - continue to interface with note object like above
        #              (consistency is good for testing purpose)
        # Get the data and annotations from the Note objects
        data   = note.getTokenizedSentences()

        # Predict IOB labels
        iobs,_,__ = self.first_predict(data)
        note.setIOBLabels(iobs)



        ###############
        # Second pass #
        ###############


        print 'second pass'

        # Get the data and annotations from the Note objects
        chunks = note.getChunkedText()
        inds   = note.getConceptIndices()

        # Predict concept labels
        retVal = self.second_predict(chunks,inds)


        return retVal




    def first_predict(self, data):

        """
        Model::first_predict()

        Purpose: Predict IOB chunks on data

        @param data.  A list of split sentences    (1 sent = 1 line from file)
        @return       A list of list of IOB labels (1:1 mapping with data)
        """

        print '\textracting  features (pass one)'


        # Create object that is a wrapper for the features
        feat_obj = features.FeatureWrapper(data)


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


        # Classify both prose & nonprose
        flabels = ['prose'             , 'nonprose'             ]
        fsets   = [prose               , nonprose               ]
        dvects  = [self.first_prose_vec, self.first_nonprose_vec]
        clfs    = [self.first_prose_clf, self.first_nonprose_clf]
        preds   = []

        for flabel,fset,dvect,clf in zip(flabels, fsets, dvects, clfs):

            # If nothing to predict, skip actual prediction
            if len(fset) == 0:
                preds.append([])
                continue


            print '\tvectorizing features (pass one) ' + flabel

            # Save list structure to reconstruct after vectorization
            offsets = [ len(sublist) for sublist in fset ]
            for i in range(1, len(offsets)):
                offsets[i] += offsets[i-1]

            # Vectorize features
            flattened = [item for sublist in fset for item in sublist]
            X = dvect.transform(flattened)


            print '\tpredicting    labels (pass one) ' + flabel

            # CRF requires reconstruct lists
            if self.crf_enabled:
                X = list(X)
                X = [ X[i:j] for i, j in zip([0] + offsets, offsets)]
                lib = crf
            else:
                lib = sci

            # Predict IOB labels
            out = lib.predict(clf, X)

            # Format labels from output
            pred = [out[i:j] for i, j in zip([0] + offsets, offsets)]
            preds.append(pred)


        # Recover predictions
        plist = preds[0]
        nlist = preds[1]


        # Stitch prose and nonprose data back together
        # translate IOB labels into a readable format
        prose_iobs    = []
        nonprose_iobs = []
        iobs          = []
        trans = lambda l: reverse_IOB_labels[int(l)]
        for sentence in data:
            if utilities.prose_sentence(sentence):
                prose_iobs.append( plist.pop(0) )
                prose_iobs[-1] = map(trans, prose_iobs[-1])
                iobs.append( prose_iobs[-1] )
            else:
                nonprose_iobs.append( nlist.pop(0) )
                nonprose_iobs[-1] = map(trans, nonprose_iobs[-1])
                iobs.append( nonprose_iobs[-1] )


        # list of list of IOB labels
        return iobs, prose_iobs, nonprose_iobs




    def second_predict(self, data, inds_list):

        # If first pass predicted no concepts, then skip
        # NOTE: Special case because SVM cannot have empty input
        if sum([ len(inds) for inds in inds_list ]) == 0:
            return []


        # Create object that is a wrapper for the features
        feat_o = features.FeatureWrapper()


        print '\textracting  features (pass two)'


        # Extract features
        X = [ feat_o.concept_features(s,inds) for s,inds in zip(data,inds_list) ]
        X = reduce(concat, X)


        print '\tvectorizing features (pass two)'


        # Vectorize features
        X = self.second_vec.transform(X)


        print '\tpredicting    labels (pass two)'


        # Predict concept labels
        out = sci.predict(self.second_clf, X)


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
                    start += len( data[lineno][i].split() )

                # Length of chunk
                length = len(data[lineno][ind].split())

                # Classification token
                classifications.append( (concept,lineno+1,start,start+length-1) )

        # Return classifications
        return classifications




def first_pass_features_and_labels(notes):

    '''
    first_pass_features_and_labels()

    Purpose: Interface with notes object to get text data and labels

    @param notes
    @return <tuple> whose elements are:
              0) list of tokenized sentences
              1) list of labels for tokenized sentences

    >>> ...
    >>> notes = ...
    >>> first_pass_features_and_labels(notes)
    (kerbkker,venrkvjdfkjv)
    '''

    # Get the data and annotations from the Note objects
    text    = [  note.getTokenizedSentences()  for  note  in  notes  ]
    ioblist = [  note.getIOBLabels()           for  note  in  notes  ]

    data1 = reduce( concat,    text )
    Y1    = reduce( concat, ioblist )

    return data1, Y1



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




def concat(a,b):
    """
    list concatenation function (for reduce() purpose)
    """
    return a+b
