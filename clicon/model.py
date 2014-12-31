from __future__ import with_statement

import os
import cPickle as pickle
import helper
import sys
from collections import defaultdict

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

        # Third pass trained
        self.is_third = False

        # DictVectorizers
        self.first_prose_vec    = DictVectorizer()
        self.first_nonprose_vec = DictVectorizer()
        self.second_vec         = DictVectorizer()
        self.third_vec          = DictVectorizer()

        # Classifiers
        self.first_prose_clf    = None
        self.first_nonprose_clf = None
        self.second_clf         = None
        self.third_clf          = None



    def train(self, notes, do_grid=False, third=False):

        """
        Model::train()

        Purpose: Train a ML model on annotated data

        @param notes    list of Note objects (containing text and annotations)
        @param do_grid  indicates whether to perform grid search
        @param third    indicates whether to perform third/clustering pass
        @return       None
        """


        ##############
        # First pass #
        ##############

        # Get the data and annotations from the Note objects
        text    = [  note.getTokenizedSentences()  for  note  in  notes  ]
        ioblist = [  note.getIOBLabels()           for  note  in  notes  ]

        data1 = reduce( concat,    text )
        Y1    = reduce( concat, ioblist )


        # Train classifier (side effect - saved as object's member variable)
        print 'first pass'
        self.first_train(data1, Y1, do_grid)



        ###############
        # Second pass #
        ###############

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

        ##############
        # Third pass #
        ##############

#        file = open("getNonContiguousSpans.log", "w")

        if third:

            print note.data

            # Set indicator to True
            self.is_third = True

            # Get data and annotations of which spans actaully should be grouped
            classifications = []
            chunks = []
            for note in notes:

            #    try:

                # Annotations for groups
                seen = len(chunks)
                non_offset = note.getNonContiguousSpans()
                offset = [ (c[0],c[1]+seen,c[2]) for c in non_offset ]
                classifications += offset

                # Chunked text
                chunks += note.getChunkedText()
            """
                except:
                    file.write("Exception: ")
                    file.write(str(sys.exc_info()))
                    file.write('\n')
                    file.write("File: " + note.txtPath + '\n')

            file.close()
            """
            #file = open("traing_error.log", "w")

            #try:

#            print "INDICESSSSSSS:", note.getConceptIndices()

            # Data of all candidates
  

            indices = [  note.getConceptIndices()  for  note  in  notes  ]
  
#            print "INDICESSSS:", indices

            inds  = reduce( concat, indices )

            # Train classifier (side effect - saved as object's member variable)
            print 'third pass'

            #print "pickling chunks"
            #chunkedDataFilePath = "/data1/kwacome/clicon_home/CliCon/CHUNKED_TRAINING_DATA/chunked_training_data.p"            

            #pickle.dump( chunks, open( chunkedDataFilePath, "wb" ) )

            self.third_train(chunks, classifications, inds, do_grid)
            """
            except:
                file.write("Exception: ")
                file.write(str(sys.exc_info()))
                file.write('\n')
                file.write("File: " + note.txtPath + '\n')
            """



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
        flabels    = ['prose'             , 'nonprose'             ]
        fsets      = [prose               , nonprose               ]
        chunksets  = [pchunks             , nchunks                ]
        dvects     = [self.first_prose_vec, self.first_nonprose_vec]
        clfs       = [self.first_prose_clf, self.first_nonprose_clf]

        vectorizers = []
        classifiers = []

        for flabel,fset,chunks,dvect,clf in zip(flabels, fsets, chunksets, dvects, clfs):

            if len(fset) == 0:

                 # no training data available. create dummy data.

                 Y = ['None']
                 X = [{'dummy':1}]

                 X = dvect.fit_transform(X)
                 vectorizers.append(dvect)

                 clf  = sci.train(X, Y, do_grid)
                 classifiers.append(clf)

                 continue

#                raise Exception('Training data must have {0} training examples'.format(flabel))

            print '\tvectorizing features (pass one) ' + flabel

            # Vectorize IOB labels
            Y = [  IOB_labels[y]  for  y  in  chunks  ]

            # Save list structure to reconstruct after vectorization
            offsets = [ len(sublist) for sublist in fset ]
            for i in range(1, len(offsets)):
                offsets[i] += offsets[i-1]

            # Vectorize features
            flattened = [item for sublist in fset for item in sublist]
            #print flattened

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




    def third_train(self, chunks, classifications, inds, do_grid=False):

        # Useful for encoding annotations
        # query line number & chunk index to get list of shared chunk indices
        relations = defaultdict(lambda:defaultdict(lambda:[]))
        for concept,lineno,spans in classifications:
            for i in range(len(spans)):
                key = spans[i]
                for j in range(len(spans)):
                    if i == j: continue
                    relations[lineno][key].append(spans[j])

        '''
        print chunks
        print
        print classifications
        print
        print inds
        exit()
        '''

#        print '\textracting  features (pass three)'

        # Create object that is a wrapper for the features
        feat_obj = features.FeatureWrapper()

#        print "inds in third_train:",inds

        # Extract features between pairs of chunks
        unvectorized_X = feat_obj.extract_third_pass_features(chunks, inds)

#        print "unvectorized_X in third_train:", unvectorized_X

        print '\tvectorizing features (pass three)'

        # Construct boolean vector of annotations
        Y = []

        for lineno,indices in enumerate(inds):
            # Cannot have pairwise relationsips with either 0 or 1 objects
            if len(indices) < 2: continue

            # Build (n choose 2) booleans
            bools = []
            for i in range(len(indices)):
                for j in range(i+1,len(indices)):
                    # Does relationship exist between this pair?
                    if indices[j] in relations[lineno][indices[i]]:
                        #print indices[i], indices[j]
                        shared = 1
                    else:
                        shared = 0
                    # Positive or negative result for training
                    bools.append(shared)

            Y += bools

        # Vectorize features
        X = self.third_vec.fit_transform(unvectorized_X)

        print '\ttraining classifier  (pass three)'

        # Train classifier
        #print Y
        self.third_clf = sci.train(X, Y, do_grid, default_label=0)



        
    # Model::predict()
    #
    # @param note. A Note object that contains the data
    def predict(self, note, third):


        ##############
        # First pass #
        ##############


        print 'first pass'

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
        classifications = self.second_predict(chunks,inds)

        ##############
        # Third pass #
        ##############

        # Third pass enabled?
        if third and self.is_third:
            print 'third pass'
            clustered = self.third_predict(chunks, classifications, inds)
        else:
            # Treat each as its own set of spans (each set containing one tuple)
            clustered = [ (c[0],c[1],[(c[2],c[3])]) for c in classifications ]

        #print clustered
        #exit()

        return clustered




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




    def third_predict(self, chunks, classifications, inds):

        print '\textracting  features (pass three)'

        # Create object that is a wrapper for the features
        feat_obj = features.FeatureWrapper(third=True)

        # Extract features between pairs of chunks
        unvectorized_X = feat_obj.extract_third_pass_features(chunks, inds)


        print '\tvectorizing features (pass three)'

        # Vectorize features
        X = self.third_vec.transform(unvectorized_X)



        print '\tpredicting    labels (pass three)'

        # Predict concept labels
        predicted_relationships = sci.predict(self.third_clf, X)

        #print predicted_relationships
        #print inds

        # TODO: Create clustered spans using predictions
        #print predicted_relationships

        classifications_cpy = list(classifications)

        # Stitch SVM output into clustered token span classifications
        clustered = []
        for indices in inds:

            # Cannot have pairwise relationsips with either 0 or 1 objects
            if len(indices) == 0: 
                continue

            elif len(indices) == 1:
                # Contiguous span (adjust format to (length-1 list of tok spans)
                tup = list(classifications_cpy.pop(0))
                tup = (tup[0],tup[1],[(tup[2],tup[3])])
                clustered.append(tup)

                #print 'single: ', indices
                #print tup
                #print

            else:

                # FIXME - cluster from output
                #print 'larger: ', indices

                # Number of classifications on the line
                tups = []
                for _ in range(len(indices)):
                    tup = list(classifications_cpy.pop(0))
                    tup = (tup[0],tup[1],[(tup[2],tup[3])])
                    tups.append(tup)

                # Pairwise clusters
                clusters = {}

                # ASSUMPTION: All classifications have same label
                concept = tups[0][0]   
                lineno = tups[0][1]
                spans = map(lambda t:t[2][0], tups)

                # Keep track of non-clustered spans
                singulars = list(tups)

                #print tups
                #print spans

                # Not actually the right update (does no clustering)

                # Get all pairwise relationships for the line
                #pairs = []
                for i in range(len(indices)):
                    for j in range(i+1,len(indices)):
                        pair = predicted_relationships.pop(0)
                        #pairs.append(pair)
                        if pair == 1:
                            #print '\t', indices[i], indices[j]
                            #print '\t\t', lineno, spans[i], spans[j]
                            tup = (concept,lineno,[spans[i],spans[j]])
                            clustered.append(tup)

                            # No longer part of a singular span
                            if tups[i] in singulars:
                                #print 'removing: ', tups[i]
                                singulars.remove(tups[i])
                            if tups[j] in singulars:
                                #print 'removing: ', tups[j]
                                singulars.remove(tups[j])

                clustered += singulars

                #print pairs
                #print

        #print classifications
        #print
        #print clustered
        #print
        #exit()
        #print clustered
        return clustered





def concat(a,b):
    """
    list concatenation function (for reduce() purpose)
    """
    return a+b
