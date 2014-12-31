######################################################################
#  CliCon - sentence_features.py                                     #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Isolate the model's sentence-level features              #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Apr. 27, 2014'



import nltk
import re
import sys
import os

from wordshape import getWordShapes

# What modules are available
from read_config import enabled_modules

# Import feature modules
enabled = enabled_modules()
if enabled['GENIA']:
    from genia_dir.genia_features import GeniaFeatures

if enabled['UMLS']:
    from umls_dir.umls_features import UMLSFeatures

from word_features import WordFeatures
from stanfordNLP import stanfordParse
from stanfordNLP import dependency_cache
from umls_dir import interface_umls

sys.path.append((os.environ["CLICON_DIR"] + "/clicon/normalization/spellCheck"))

from spellChecker import getPWL

class SentenceFeatures:


    # Feature Enabling

    enabled_concept_features = frozenset( ["UMLS"])



    # Instantiate an Sentence object
    def __init__(self, data, third=False):

        # Word-level features module
        self.feat_word = WordFeatures()

        # Only run GENIA tagger if module is available
        if data and enabled['GENIA']:
            tagger = enabled['GENIA']
            self.feat_genia = GeniaFeatures(tagger,data)

        # Only create UMLS cache if module is available
        if enabled['UMLS']:
            self.feat_umls = UMLSFeatures()


        self.enabled_IOB_nonprose_sentence_features = []
        #self.enabled_IOB_nonprose_sentence_features.append('pos')
        #self.enabled_IOB_nonprose_sentence_features.append('pos_context')
        self.enabled_IOB_nonprose_sentence_features.append('prev')
        self.enabled_IOB_nonprose_sentence_features.append('next')
        self.enabled_IOB_nonprose_sentence_features.append('unigram_context')
        self.enabled_IOB_nonprose_sentence_features.append('UMLS')

        self.enabled_IOB_prose_sentence_features = []
        self.enabled_IOB_prose_sentence_features.append('unigram_context')
        self.enabled_IOB_prose_sentence_features.append('pos')
        self.enabled_IOB_prose_sentence_features.append('pos_context')
        self.enabled_IOB_prose_sentence_features.append('prev')
        self.enabled_IOB_prose_sentence_features.append('prev2')
        self.enabled_IOB_prose_sentence_features.append('next')
        self.enabled_IOB_prose_sentence_features.append('next2')
        self.enabled_IOB_prose_sentence_features.append('GENIA')
        self.enabled_IOB_prose_sentence_features.append('UMLS')

        if third is True:
            self.dependencyCache = dependency_cache.DependencyCache()
            self.pwl = getPWL()

    # IOB_prose_features()
    #
    # input:  A sentence
    # output: A list of hash tables of features
    def IOB_prose_features(self, sentence):

        features_list = []

        # Get a feature set for each word in the sentence
        for i,word in enumerate(sentence):
            features_list.append(self.feat_word.IOB_prose_features(sentence[i]))


        # Feature: Bag of Words unigram conext (window=3)
        if 'unigram_context' in self.enabled_IOB_prose_sentence_features:
            window = 3
            n = len(sentence)

            # Previous unigrams
            for i in range(n):
                end = min(i, window)
                unigrams = sentence[i-end:i]
                for j,u in enumerate(unigrams):
                    features_list[i][('prev_unigrams-%d'%j,u)] = 1

            # Next     unigrams
            for i in range(n):
                end = min(i + window, n-1)
                unigrams = sentence[i+1:end+1]
                for j,u in enumerate(unigrams):
                    features_list[i][('next_unigrams-%d'%j,u)] = 1


        # Only POS tag once
        if 'pos' in self.enabled_IOB_prose_sentence_features:
            pos_tagged = nltk.pos_tag(sentence)


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_prose_sentence_features:


            # Feature: Part of Speech
            if feature == 'pos':
                for (i,(_,pos)) in enumerate(pos_tagged):
                    features_list[i].update( { ('pos',pos) : 1} )


            # Feature: POS context
            if 'pos_context' in self.enabled_IOB_prose_sentence_features:
                window = 3
                n = len(sentence)

                # Previous POS
                for i in range(n):
                    end = min(i, window)
                    for j,p in enumerate(pos_tagged[i-end:i]):
                        pos = p[1]
                        features_list[i][('prev_pos_context-%d'%j,pos)] = 1

                # Next POS
                for i in range(n):
                    end = min(i + window, n-1)
                    for j,p in enumerate(pos_tagged[i+1:i+end+1]):
                        pos = p[1]
                        features_list[i][('prev_pos_context-%d'%j,pos)] = 1


            # GENIA features
            if (feature == 'GENIA') and enabled['GENIA']:

                # Get GENIA features
                genia_feat_list = self.feat_genia.features(sentence)

                '''
                print '\t', sentence

                print '\n\n'
                for gf in genia_feat_list:
                    print '\t', gf
                    print
                print '\n\n'
                '''

                for i,feat_dict in enumerate(genia_feat_list):
                    features_list[i].update(feat_dict)

                
            # Feature: UMLS Word Features (only use prose ones)
            if (feature == "UMLS") and enabled['UMLS']:
                umls_features = self.feat_umls.IOB_prose_features(sentence)
                for i in range(len(sentence)):
                    features_list[i].update( umls_features[i] )


        # Used for 'prev' and 'next' features
        ngram_features = [{} for i in range(len(features_list))]
        if "prev" in self.enabled_IOB_prose_sentence_features:
            prev = lambda f: {("prev_"+k[0], k[1]): v for k,v in f.items()}
            prev_list = map(prev, features_list)
            for i in range(len(features_list)):
                if i == 0:
                    ngram_features[i][("prev", "*")] = 1
                else:
                    ngram_features[i].update(prev_list[i-1])

        if "prev2" in self.enabled_IOB_prose_sentence_features:
            prev2 = lambda f: {("prev2_"+k[0], k[1]): v/2.0 for k,v in f.items()}
            prev_list = map(prev2, features_list)
            for i in range(len(features_list)):
                if i == 0:
                    ngram_features[i][("prev2", "*")] = 1
                elif i == 1:
                    ngram_features[i][("prev2", "*")] = 1
                else:
                    ngram_features[i].update(prev_list[i-2])

        if "next" in self.enabled_IOB_prose_sentence_features:
            next = lambda f: {("next_"+k[0], k[1]): v for k,v in f.items()}
            next_list = map(next, features_list)
            for i in range(len(features_list)):
                if i < len(features_list) - 1:
                    ngram_features[i].update(next_list[i+1])
                else:
                    ngram_features[i][("next", "*")] = 1

        if "next2" in self.enabled_IOB_prose_sentence_features:
            next2 = lambda f: {("next2_"+k[0], k[1]): v/2.0 for k,v in f.items()}
            next_list = map(next2, features_list)
            for i in range(len(features_list)):
                if i < len(features_list) - 2:
                    ngram_features[i].update(next_list[i+2])
                elif i == len(features_list) - 2:
                    ngram_features[i][("next2", "**")] = 1
                else:
                    ngram_features[i][("next2", "*")] = 1

        merged = lambda d1, d2: dict(d1.items() + d2.items())
        features_list = [merged(features_list[i], ngram_features[i]) 
            for i in range(len(features_list))]


        '''
        for f in features_list:
            print sorted(f.items())
            print
        print '\n\n\n'
        '''

        return features_list



    # IOB_nonprose_features()
    #
    # input:  A sentence
    # output: A hash table of features
    def IOB_nonprose_features(self, sentence):


        # Get a feature set for each word in the sentence
        features_list = []
        for i,word in enumerate(sentence):
            word_feats = self.feat_word.IOB_nonprose_features(sentence[i])
            features_list.append( word_feats )


        # Feature: Bag of Words unigram conext (window=3)
        if 'unigram_context' in self.enabled_IOB_nonprose_sentence_features:
            window = 3
            n = len(sentence)

            # Previous unigrams
            for i in range(n):
                end = min(i, window)
                unigrams = sentence[i-end:i]
                for j,u in enumerate(unigrams):
                    features_list[i][('prev_unigrams-%d'%j,u)] = 1

            # Next     unigrams
            for i in range(n):
                end = min(i + window, n-1)
                unigrams = sentence[i+1:end+1]
                for u in unigrams:
                    features_list[i][('next_unigrams-%d'%j,u)] = 1


        # Feature: UMLS Word Features (only use nonprose ones)
        if enabled['UMLS'] and 'UMLS' in self.enabled_IOB_nonprose_sentence_features:
            umls_features = self.feat_umls.IOB_nonprose_features(sentence)
            for i in range(len(sentence)):
                features_list[i].update( umls_features[i] )


        #return features_list

        if 'pos' in self.enabled_IOB_nonprose_sentence_features:
            pos_tagged = nltk.pos_tag(sentence)


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_nonprose_sentence_features:

            # Feature: Part of Speech
            if feature == 'pos':
                for (i,(_,pos)) in enumerate(pos_tagged):
                    features_list[i][ ('pos',pos) ] = 1


            # Feature: POS context
            if 'pos_context' in self.enabled_IOB_nonprose_sentence_features:
                window = 3
                n = len(sentence)

                # Previous POS
                for i in range(n):
                    end = min(i, window)
                    for j,p in enumerate(pos_tagged[i-end:i]):
                        pos = p[1]
                        features_list[i][('prev_pos_context-%d'%j,pos)] = 1

                # Next POS
                for i in range(n):
                    end = min(i + window, n-1)
                    for j,p in enumerate(pos_tagged[i+1:i+end+1]):
                        pos = p[1]
                        features_list[i][('prev_pos_context-%d'%j,pos)] = 1



        ngram_features = [{} for _ in range(len(features_list))]
        if "prev" in self.enabled_IOB_nonprose_sentence_features:
            prev = lambda f: {("prev_"+k[0], k[1]): v for k,v in f.items()}
            prev_list = map(prev, features_list)
            for i in range(len(features_list)):
                if i == 0:
                    ngram_features[i][("prev", "*")] = 1
                else:
                    ngram_features[i].update(prev_list[i-1])

        if "next" in self.enabled_IOB_nonprose_sentence_features:
            next = lambda f: {("next_"+k[0], k[1]): v for k,v in f.items()}
            next_list = map(next, features_list)
            for i in range(len(features_list)):
                if i == len(features_list) - 1:
                    ngram_features[i][("next", "*")] = 1
                else:
                    ngram_features[i].update(next_list[i+1])


        merged = lambda d1, d2: dict(d1.items() + d2.items())
        features_list = [merged(features_list[i], ngram_features[i]) 
            for i in range(len(features_list))]


        return features_list




    def concept_features_for_sentence(self, sentence, chunk_inds):

        #print "called concept_features_for_sentence"
        """
        concept_features()

        @param  sentence.   A sentence in list of chunk format
        @param  chunk_inds. A list of indices for non-None-labeled chunks
        @return             A list of feature dictionaries
        """
        print "called concept_features_for_sentence"

        #print "sentence in concept_features_for_sentence", sentence
        #print "chunk_inds in concept_features_for_sentence:", chunk_inds

        # Get a feature set for each word in the sentence
        features_list = []
        for ind in chunk_inds:
            features_list.append( self.feat_word.concept_features_for_chunk(sentence,ind) )

        #print "features_list after first for loop:", features_list

        # Allow for particular features to be enabled
        for feature in self.enabled_concept_features:

            # Features: UMLS features
            if (feature == "UMLS") and enabled['UMLS']:
                umls_features = self.feat_umls.concept_features_for_chunks(sentence, chunk_inds)
                for i in range(len(chunk_inds)):
                    features_list[i].update( umls_features[i] )

        #print "returned features_list:", features_list
        return features_list

    def getDependencyPaths(self, line):

        retVal = None

        string = ' '.join(line)

        if self.dependencyCache.has_key(string) is True:

            retVal = self.dependencyCache.get_map(string)

        else:

            paths = stanfordParse.getDepenPaths(string)

            self.dependencyCache.add_map(string, paths)

            retVal = paths

        return retVal

    def getTypesOfRel(self, start, end, groupsOfPaths):
        """
        returns a list of list of tokens indicating the types of relations between

        dependencies.
        """

        lOflOfRelations = []

        lOflOfTokens = stanfordParse.followDependencyPath(start, end, groupsOfPaths)

        for l in lOflOfTokens:
            # get relations from ordered token list
            tmpL = [tok for tok in l if '__relation' in tok]

            lOflOfRelations.append(tmpL)

#        print lOflOfRelations
        return self.getShortestList( lOflOfRelations )

    def getTokens(self, start, end, groupsOfPaths):

        lOflOfSpans = []

        lOflOfTokens = stanfordParse.followDependencyPath(start, end, groupsOfPaths)

        for l in lOflOfTokens:
            # get spans from ordered token list
            tmpL = [tok for tok in l if '__relation' not in tok]

            lOflOfSpans.append(tmpL)

#        print lOflOfSpans
        return self.getShortestList(lOflOfSpans)

    def getNumOfObjects(self, lOfObjects):
        return len( lOfObjects )
 
    def getShortestList(self, lOflOfl):

        shortestL = []
 
        for l in lOflOfl:

            if len(shortestL) is 0:
                shortestL = l
            elif len(l) < len(shortestL):
                shortestL = l

        return shortestL

    def third_pass_features(self, line, indices):
        print "third_pass_features called"
        # Cannot have pairwise relationsips with either 0 or 1 objects
        if len(indices) < 2: 
            return []

        else:

            # get dependency paths for tokens in line.
            groupsOfPaths = self.getDependencyPaths(line)

        features_list = []

        # Build (n choose 2) booleans
        for i in range(len(indices)):
            for j in range(i+1,len(indices)):

                start = line[indices[i]]
                end = line[indices[j]]

                # Features of pair relationship
                feats = {}

                """
                print "LINE:"
                print line
                print "indices:"
                print indices
                print "START TOKEN:"
                print "i: ", i
                print start
                print "END TOKEN:"
                print "j: ", j
                print end
 
                print "RELATIONS BETWEEN DEPENDENCIES:"
                """

                lOfRels = self.getTypesOfRel(start, end, groupsOfPaths)

                numOfRels = self.getNumOfObjects(lOfRels)

#                print lOflOfRels

                lOfTokes = self.getTokens(start, end, groupsOfPaths)

                numOfTokes = self.getNumOfObjects( lOfTokes )

#                print "TOKENS BETWEEN DEPENDENCIES:"
#                print lOfTokes

                for tokeIndex, _ in enumerate(lOfTokes):
                    if tokeIndex != (len(lOfTokes) - 1):
#                        print (lOfTokes[i], lOfTokes[i+1])
                        feats[('toks_btwn_depen', (lOfTokes[tokeIndex], lOfTokes[tokeIndex+1]))] = 1
                    else:
                        break

                for rel in lOfRels:
                    feats[('rels_btwn_depen', rel)] = 1

                feats[('num_of_rels', None)] = numOfRels
                feats[('num_of_depen_tokes', None)] = (numOfTokes - 2 if numOfTokes != 0 else numOfTokes)

                feats[("tokes_that_exists_in_umls_db",None)] = interface_umls.substrs_that_exists([start, end], self.pwl)

                # Feature: Left Unigrams
                for tok in line[indices[i]].split():
                    tok = tok.lower()
                    feats[('left_unigram' ,tok)] = 1

                # Feature: Right Unigrams
                for tok in line[indices[j]].split():
                    tok = tok.lower()
                    feats[('right_unigram',tok)] = 1

                # Feature: Unigrams between spans
                for tok in ' '.join(line[indices[i+1]:indices[j]]).split():
                    tok = tok.lower()
                    feats[('inner_unigram',tok)] = 1
                
                # Feature: Number of chunks between spans
                feats[('span_dist',None)] = len(line[indices[i+1]:indices[j]])
              

                # Add pair features to list of data points
                features_list.append(feats)

        return features_list
