######################################################################
#  CliCon - clicon_features.py                                       #
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
    def __init__(self, data=None):

        # Sentence-level features
        self.feat_sent = SentenceFeatures(data)



    # IOB_features()
    #
    # input:  A sentence
    # output: A hash table of features
    def IOB_features(self, sentence):

        # Different features depending on whether sentence is 'prose'
        isProse = prose_sentence(sentence)

        unique =  1 # 20

        if isProse:
            if True:
                features_list = self.feat_sent.IOB_prose_features(sentence)
            else:
                # Sanity Check (many unique features for each data point)
                features_list = []
                for i in range(len(sentence)):
                    features = {}
                    for j in range(unique):
                        features[(''.join(sentence),i,j)] = 1
                    features_list.append(features)
        else:
            if False:
                features_list = self.feat_sent.IOB_nonprose_features(sentence)
            else:
                # Sanity Check (many unique features for each data point)
                features_list = []
                for i in range(len(sentence)):
                    features = {}
                    for j in range(unique):
                        features[(''.join(sentence),i,j)] = 1
                    features_list.append(features)


        #'''
        for f in features_list:
            print sorted(f.items())
            print 
        #'''


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

