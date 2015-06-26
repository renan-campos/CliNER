######################################################################
#  CliNER - model.py                                                 #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: CliNER Model object that encapsulates the parameters.    #
######################################################################


from __future__ import with_statement


__author__ = 'Willie Boag'
__date__   = 'June 23, 2015'



import sys

from sklearn.feature_extraction  import DictVectorizer

from features_dir.features import FeatureWrapper
from features_dir.utilities import load_pickled_obj, is_prose_sentence

from machine_learning import sci
from machine_learning import crf

from notes.note import concept_labels, reverse_concept_labels, IOB_labels, reverse_IOB_labels


class Model:

    @staticmethod
    def load(filename='default_cliner.model'):

        model = load_pickled_obj(filename)
        model.filename = filename

        return model



    def __init__(self, is_crf=True):

        # Use python-crfsuite
        self._crf_enabled = is_crf

        # DictVectorizers
        self._first_prose_vec    = DictVectorizer()
        self._first_nonprose_vec = DictVectorizer()
        self._second_vec         = DictVectorizer()

        # Classifiers
        self._first_prose_clf    = None
        self._first_nonprose_clf = None
        self._second_clf         = None



    def train(self, notes, do_grid=False, out_handle=sys.stdout):

        """
        Model::train()

        Purpose: Train a ML model on annotated data

        @param notes. A list of Note objects (containing text and annotations)
        @return       None

        >>> import os
        >>> base_dir   = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
        >>> txt_file   = os.path.join(base_dir,'multi.txt')
        >>> con_file   = os.path.join(base_dir,'multi.con')
        >>> empty_file = os.path.join(base_dir,'empty.con')

        >>> from notes.note import Note
        >>> import tempfile
        >>> import filecmp


        >>> note2 = Note('i2b2')
        >>> note2.read(txt_file, empty_file)
        >>> notes = [note2]

        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> out_handle = open(out_file, 'w')
        >>> model = Model(is_crf=True)
        >>> model.train(notes, do_grid=False, out_handle=out_handle)
        Traceback (most recent call last):
          ...
        AssertionError: Given 0 labels. Must have label set for training


        >>> note = Note('i2b2')
        >>> note.read(txt_file, con_file)
        >>> notes = [note]

        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> out_handle = open(out_file, 'w')
        >>> model = Model(is_crf=True)
        >>> model.train(notes, do_grid=False, out_handle=out_handle)

        >>> out_handle.close()
        >>> expected_file = os.path.join(base_dir,'expected_train.txt')
        >>> filecmp.cmp(expected_file, out_file)
        True
        >>> os.close(os_handle)
        """

        ##############
        # First pass #
        ##############

        # Get the data and annotations from the Note objects
        text    = [  note.getTokenizedSentences()  for  note  in  notes  ]
        ioblist = [  note.getIOBLabels()           for  note  in  notes  ]

        data1 = sum(text   , [])
        Y1    = sum(ioblist, [])

        # Train classifier (side effect - saved as object's member variable)
        print >>out_handle, 'first pass'
        self.__first_train(data1, Y1, do_grid, out_handle)


        ###############
        # Second pass #
        ###############

        # Get the data and annotations from the Note objects
        chunks  = [  note.getChunkedText()     for  note  in  notes  ]
        indices = [  note.getConceptIndices()  for  note  in  notes  ]
        conlist = [  note.getConceptLabels()   for  note  in  notes  ]

        data2 = sum(chunks ,[])
        inds  = sum(indices,[])
        Y2    = sum(conlist,[])

        # Train classifier (side effect - saved as object's member variable)
        print >>out_handle, 'second pass'
        self.__second_train(data2, inds, Y2, do_grid, out_handle)



    def test_first_train(self, data, Y, do_grid, out_handle):

        """
        Model::test_first_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data      A list of split sentences    (1 sent = 1 line from file)
        @param Y         A list of list of IOB labels (1:1 mapping with data)
        @param do_grid   A boolean indicating whether to perform a grid search
        @return          None

        >>> import tempfile
        >>> import os


        >>> data = [['Title', ':'], ['Casey', 'at', 'the', 'Bat'], ['The', 'outlook', "wasn't", 'brilliant', 'for', 'the', 'Mudville', 'Nine', 'that', 'day', ';'], ['The', 'score', 'stood', 'four', 'to', 'two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']]
        >>> Y = [['O', 'O'], ['B', 'I', 'I', 'I'], ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'], ['B', 'I', 'I', 'I', 'I', 'I', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']]
        >>> model = Model(is_crf=False)
        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> out_handle = open(out_file, 'w')
        >>> model.test_first_train(data, Y, do_grid=False, out_handle=out_handle)
        >>> out_handle.close()
        >>> os.close(os_handle)


        >>> data2 = []
        >>> Y2    = []
        >>> model2 = Model(is_crf=False)
        >>> os_handle2,out_file2 = tempfile.mkstemp(dir='/tmp')
        >>> out_handle2 = open(out_file2, 'w')
        >>> model.test_first_train(data2, Y, do_grid=False, out_handle=out_handle2)
        Traceback (most recent call last):
          ...
        Exception: Training data must have prose training examples

        >>> out_handle2.close()
        >>> os.close(os_handle2)
        """
        self.__first_train(data,Y,do_grid,out_handle)



    def test_second_train(self, data, inds_list, Y, do_grid, out_handle):
        '''
        Model::test_second_train()

        Purpose: Train the second pass classifiers (for concept classification)

        >>> import tempfile
        >>> import tempfile
        >>> import os


        >>> data      = []
        >>> inds_list = []
        >>> Y         = []
        >>> model = Model(is_crf=False)
        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> out_handle = open(out_file, 'w')
        >>> model.test_second_train(data,inds_list,Y,do_grid=False,out_handle=out_handle)
        Traceback (most recent call last):
          ...
        AssertionError: Given 0 labels. Must have label set for training

        >>> out_handle.close()
        >>> os.close(os_handle)


        >>> data2      = [['Title', ':'], ['Casey at the Bat'], ['The', 'outlook', "wasn't", 'brilliant', 'for', 'the', 'Mudville', 'Nine', 'that', 'day', ';'], ['The score stood four to two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']]
        >>> inds_list2 = [[], [0], [], [0]]
        >>> Y2         = ['treatment', 'problem']
        >>> model2 = Model(is_crf=False)
        >>> os_handle2,out_file2 = tempfile.mkstemp(dir='/tmp')
        >>> out_handle2 = open(out_file2, 'w')
        >>> model.test_second_train(data2, inds_list2, Y2, False, out_handle2)
        >>> out_handle2.close()
        >>> os.close(os_handle2)
        '''
        self.__second_train(data, inds_list, Y, do_grid, out_handle)




    def __first_train(self, data, Y, do_grid, out_handle):

        """
        Model::__first_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data      A list of split sentences    (1 sent = 1 line from file)
        @param Y         A list of list of IOB labels (1:1 mapping with data)
        @param do_grid   A boolean indicating whether to perform a grid search
        @return          None

        Note: Cannot test directly because private method. See test_first_train() for tests
        """

        print >>out_handle, '\textracting  features (pass one)'

        # Create object that is a wrapper for the features
        feat_obj = FeatureWrapper(data)

        # Parition into prose v. nonprose
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

        # Classify both prose & nonprose
        flabels    = ['prose'              , 'nonprose'             ]
        fsets      = [prose                , nonprose               ]
        chunksets  = [pchunks              , nchunks                ]
        dvects     = [self._first_prose_vec, self._first_nonprose_vec]
        clfs       = [self._first_prose_clf, self._first_nonprose_clf]

        vectorizers = []
        classifiers = []
        for flabel,fset,chunks,dvect,clf in zip(flabels, fsets, chunksets, dvects, clfs):

            if len(fset) == 0:
                raise Exception('Training data must have %s training examples' % flabel)

            print >>out_handle, '\tvectorizing features (pass one) ' + flabel

            # Vectorize IOB labels
            Y = [ IOB_labels[y] for y in chunks ]

            # Save list structure to reconstruct after vectorization
            offsets = [ len(sublist) for sublist in fset ]
            for i in range(1, len(offsets)):
                offsets[i] += offsets[i-1]

            # Vectorize features
            flattened = [item for sublist in fset for item in sublist]
            X = dvect.fit_transform(flattened)
            vectorizers.append(dvect)

            print >>out_handle, '\ttraining classifiers (pass one) ' + flabel

            # CRF needs reconstructed lists
            if self._crf_enabled:
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
        self._first_prose_vec    = vectorizers[0]
        self._first_nonprose_vec = vectorizers[1]

        # Save classifiers
        self._first_prose_clf    = classifiers[0]
        self._first_nonprose_clf = classifiers[1]



    def __second_train(self, data, inds_list, Y, do_grid, out_handle):

        """
        Model::__second_train()

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

        Note: Cannot test directly because private method. See test_first_train() for tests
        """

        assert len(Y)>0, Exception('Given 0 labels. Must have label set for training')

        print >>out_handle, '\textracting  features (pass two)'

        # Create object that is a wrapper for the features
        feat_o = FeatureWrapper()

        # Extract features
        X = [ feat_o.concept_features(s,inds) for s,inds in zip(data,inds_list) ]
        X = sum(X,[])

        print >>out_handle, '\tvectorizing features (pass two)'

        # Vectorize features & labels
        Y = [ concept_labels[y] for y in Y ]
        X = self._second_vec.fit_transform(X)

        print >>out_handle, '\ttraining  classifier (pass two)'

        # Train the model
        self._second_clf = sci.train(X, Y, do_grid)




    def predict(self, note, out_handle=sys.stdout):

        '''
        Note::predict()

        Purpose: Predict labels for a note

        @param note
        @param out_handle
        @return            A list of predictions

        >>> import os
        >>> base_dir   = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
        >>> txt_file   = os.path.join(base_dir,'multi.txt')
        >>> con_file   = os.path.join(base_dir,'multi.con')
        >>> empty_file = os.path.join(base_dir,'empty.con')

        >>> from notes.note import Note
        >>> import tempfile
        >>> import filecmp

        >>> note = Note('i2b2')
        >>> note.read(txt_file, con_file)
        >>> notes = [note]

        >>> os_train_handle,out_train_file = tempfile.mkstemp(dir='/tmp')
        >>> out_train_handle = open(out_train_file, 'w')
        >>> model = Model(is_crf=True)
        >>> model.train(notes, do_grid=False, out_handle=out_train_handle)
        >>> out_train_handle.close()
        >>> expected_train_file = os.path.join(base_dir,'expected_train.txt')
        >>> filecmp.cmp(expected_train_file, out_train_file)
        True
        >>> os.close(os_train_handle)


        >>> os_predict_handle,out_predict_file = tempfile.mkstemp(dir='/tmp')
        >>> out_predict_handle = open(out_predict_file, 'w')
        >>> labels = model.predict(note, out_handle=out_predict_handle)
        >>> out_predict_handle.close()
        >>> expected_predict_file = os.path.join(base_dir,'expected_predict.txt')
        >>> filecmp.cmp(expected_predict_file, out_predict_file)
        True
        >>> os.close(os_predict_handle)

        >>> out = note.write(labels)
        >>> out_handle,output_predict_file = tempfile.mkstemp(dir='/tmp')
        >>> out_predict_handle = open(output_predict_file, 'w')
        >>> out_predict_handle.write(out)
        >>> out_predict_handle.close()
        >>> filecmp.cmp(output_predict_file, con_file)
        True
        >>> os.close(out_handle)
        '''

        ##############
        # First pass #
        ##############

        print >>out_handle, 'first pass'

        # Get the data and annotations from the Note objects
        data   = note.getTokenizedSentences()

        # Predict IOB labels
        iobs,_,__ = self.__first_predict(data, out_handle)
        note.setIOBLabels(iobs)


        ###############
        # Second pass #
        ###############

        print >>out_handle, 'second pass'

        # Get the data and annotations from the Note objects
        chunks = note.getChunkedText()
        inds   = note.getConceptIndices()

        # Predict concept labels
        retVal = self.__second_predict(chunks,inds, out_handle)

        return retVal




    def test_frst_predict(self, data, out_handle):
        '''
        Model::test_first_predict()

        Purpose: Unit tests for Model::__first_predict

        @param data
        @param out_handle


        >>> import tempfile
        >>> import os


        >>> data = [['Title', ':'], ['Casey', 'at', 'the', 'Bat'], ['The', 'outlook', "wasn't", 'brilliant', 'for', 'the', 'Mudville', 'Nine', 'that', 'day', ';'], ['The', 'score', 'stood', 'four', 'to', 'two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']]
        >>> Y = [['O', 'O'], ['B', 'I', 'I', 'I'], ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'], ['B', 'I', 'I', 'I', 'I', 'I', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']]
        >>> model = Model(is_crf=False)
        >>> os_handle,out_file = tempfile.mkstemp(dir='/tmp')
        >>> out_handle = open(out_file, 'w')
        >>> model.test_first_train(data, Y, do_grid=False, out_handle=out_handle)
        >>> out_handle.close()
        >>> os.close(os_handle)

        >>> print 4
        3


        >>> data2 = []

        '''


    def __first_predict(self, data, out_handle):

        """
        Model::__first_predict()

        Purpose: Predict IOB chunks on data

        @param data.  A list of split sentences    (1 sent = 1 line from file)
        @return       A list of list of IOB labels (1:1 mapping with data)
        """

        print >>out_handle, '\textracting  features (pass one)'

        # Create object that is a wrapper for the features
        feat_obj = FeatureWrapper(data)

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
        flabels = ['prose'              , 'nonprose'              ]
        fsets   = [prose                , nonprose                ]
        dvects  = [self._first_prose_vec, self._first_nonprose_vec]
        clfs    = [self._first_prose_clf, self._first_nonprose_clf]
        preds   = []

        for flabel,fset,dvect,clf in zip(flabels, fsets, dvects, clfs):

            # If nothing to predict, skip actual prediction
            if len(fset) == 0:
                preds.append([])
                continue

            print >>out_handle, '\tvectorizing features (pass one) ' + flabel

            # Save list structure to reconstruct after vectorization
            offsets = [ len(sublist) for sublist in fset ]
            for i in range(1, len(offsets)):
                offsets[i] += offsets[i-1]

            # Vectorize features
            flattened = [item for sublist in fset for item in sublist]
            X = dvect.transform(flattened)

            print >>out_handle, '\tpredicting    labels (pass one) ' + flabel

            # CRF requires reconstruct lists
            if self._crf_enabled:
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
            if is_prose_sentence(sentence):
                prose_iobs.append( plist.pop(0) )
                prose_iobs[-1] = map(trans, prose_iobs[-1])
                iobs.append( prose_iobs[-1] )
            else:
                nonprose_iobs.append( nlist.pop(0) )
                nonprose_iobs[-1] = map(trans, nonprose_iobs[-1])
                iobs.append( nonprose_iobs[-1] )

        # list of list of IOB labels
        return iobs, prose_iobs, nonprose_iobs




    def __second_predict(self, data, inds_list, out_handle):

        # If first pass predicted no concepts, then skip
        # NOTE: Special case because SVM cannot have empty input
        if sum([ len(inds) for inds in inds_list ]) == 0:
            print >>out_handle, "first pass predicted no concepts, skipping second pass"
            return []

        # Create object that is a wrapper for the features
        feat_o = FeatureWrapper()

        print >>out_handle, '\textracting  features (pass two)'

        # Extract features
        X = [ feat_o.concept_features(s,inds) for s,inds in zip(data,inds_list) ]
        X = sum(X,[])

        print >>out_handle, '\tvectorizing features (pass two)'

        # Vectorize features
        X = self._second_vec.transform(X)

        print >>out_handle, '\tpredicting    labels (pass two)'

        # Predict concept labels
        out = sci.predict(self._second_clf, X)

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

