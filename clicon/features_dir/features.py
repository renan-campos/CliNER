######################################################################
#  CliCon - features.py                                              #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Isolate the model's features from model.py               #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Jan. 27, 2014'



import nltk
import re

from wordshape import getWordShapes
from utilities import prose_sentence

from sentence_features import SentenceFeatures



class FeatureWrapper:

    # FIXME - Make three objects - one for each classifier


    # Instantiate an FeatureWrapper object
    def __init__(self, data=None, third=False):

        # Sentence-level features
        self.feat_sent = SentenceFeatures(data, third=third)



    # IOB_features()
    #
    # input:  A sentence
    # output: A hash table of features
    def extract_IOB_features(self, sentence):

        # Different features depending on whether sentence is 'prose'
        isProse = prose_sentence(sentence)

        if isProse:
            features_list = self.feat_sent.IOB_prose_features(sentence)
        else:
            features_list = self.feat_sent.IOB_nonprose_features(sentence)

        # Return features as well as indication of whether it is prose or not
        return (isProse, features_list)



    # concept_features()
    #
    # input:  A sentence/line from a medical text file (list of chunks)
    #         An list of indices into the sentence for each important chunk
    # output: A list of hash tables of features
    def concept_features(self, sentence, chunk_inds):
        
        # FIXME - move all of this work to SentenceFeatures object

        '''
        # VERY basic feature set for sanity check tests during development
        features_list = []
        for i,ind in enumerate(chunk_inds):
            features = {('phrase',sentence[ind]) : 1} 
            features_list.append(features)
        return features_list
        '''

        # Create a list of feature sets (one per chunk)
        features_list = self.feat_sent.concept_features_for_sentence(sentence,chunk_inds)
        return features_list



    def extract_third_pass_features(self, chunks, inds):

#        for line, ind in zip(chunks, inds):

#            for i in ind:

#                print line[i]
            #l = ' '.join(line)

            #l += '\n'

            #print l

        #print chunks
        #print inds
        """
        print "called extract_third_pass_features"

        print "inds in extract_third_pass_features:", inds
        print "chunks in extract_third_pass_features:", chunks
        """

        # not sure what this was used for but I do not see it used any where.
        #fileLines = [] 

        #f = open("STANFORD_INPUT.txt", "w")

        #for line in chunks:

        #    f.write(' '.join(line) + '\n')

        unvectorized_X = []
        for lineno,indices in enumerate(inds):

            '''
            # Cannot have pairwise relationsips with either 0 or 1 objects
            if len(indices) < 2: continue

            # Build (n choose 2) booleans
            features = []
            for i in range(len(indices)):
                for j in range(i+1,len(indices)):
                    feats = {(lineno,i):1,(lineno,j):1}

                    # Positive or negative result for training
                    features.append(feats)
            '''

            """
            print "lineno, indices"
            print lineno, indices

            print "chunk[lineno]:", chunks[lineno]
            print "indices:", indices
            """

#            print lineno
#            print len(chunks)

            features = self.feat_sent.third_pass_features(chunks[lineno],indices)

            #print "features:", features

            unvectorized_X += features

        #print "ret unvectorized_X:", unvectorized_X
        return unvectorized_X
