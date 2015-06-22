######################################################################
#  CliCon - sentence_features.py                                     #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Isolate the model's sentence-level features              #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Apr. 27, 2014'

from utilities import load_pos_tagger

from wordshape import getWordShapes

# What modules are available
from read_config import enabled_modules

enabled = enabled_modules()
if enabled['UMLS']:
    from umls_dir.umls_features import UMLSFeatures

from word_features import WordFeatures

nltk_tagger = load_pos_tagger()

class SentenceFeatures:


    # Feature Enabling

    enabled_concept_features = frozenset( ["UMLS"])



    # Instantiate an Sentence object
    def __init__(self, data):


        # Word-level features module
        self.feat_word = WordFeatures()

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
        self.enabled_IOB_prose_sentence_features.append('UMLS')



    def IOB_prose_features(self, sentence):
        """
        IOB_prose_features

        @param sentence. A list of strings
        @return          A list of dictionaries of features

        """
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
            pos_tagged = nltk_tagger.tag(sentence)

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


    def IOB_nonprose_features(self, sentence):
        """
        IOB_nonprose_features
        
        @param sentence. A list of strings
        @return          A list of dictionaries of features
        
        """
        
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
            pos_tagged = nltk_tagger.tag(sentence)

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

        """
        concept_features()

        @param  sentence.   A sentence in list of chunk format
        @param  chunk_inds. A list of indices for non-None-labeled chunks
        @return             A list of feature dictionaries
        """


        # Get a feature set for each word in the sentence
        features_list = []
        for ind in chunk_inds:
            features_list.append( self.feat_word.concept_features_for_chunk(sentence,ind) )


        # Allow for particular features to be enabled
        for feature in self.enabled_concept_features:

            # Features: UMLS features
            if (feature == "UMLS") and enabled['UMLS']:
                umls_features = self.feat_umls.concept_features_for_chunks(sentence, chunk_inds)
                for i in range(len(chunk_inds)):
                    features_list[i].update( umls_features[i] )


        return features_list


