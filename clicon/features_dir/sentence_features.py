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
from sets import ImmutableSet
from wordshape import getWordShapes



# What modules are available
from read_config import enabled_modules




# Import feature modules
enabled = enabled_modules()
if enabled['GENIA']:
    from genia.genia_features import GeniaFeatures

if enabled['UMLS']:
    from umls.umls_features import UMLSFeatures

from word_features import WordFeatures




class SentenceFeatures:


    # Feature Enabling
    #enabled_IOB_prose_sentence_features = ImmutableSet( [ 'pos', 'stem_wordnet', 'GENIA', 'prev', 'next', 'prev_3_pos', 'next_3_pos', 'UMLS'] )

    enabled_IOB_nonprose_sentence_features = ImmutableSet( ['pos', 'test_result', 'prev', 'next','prev_3_pos', 'next_3_pos', 'UMLS'])

    enabled_concept_features = ImmutableSet( ['pos','prev_3_pos', 'stem_wordnet', 'test_result', 'word_shape','prev','next', "UMLS"])



    # Instantiate an Sentence object
    def __init__(self, data):

        # Word-level features module
        self.feat_word = WordFeatures()

        # Only run GENIA tagger if module is available
        if data and enabled['GENIA']:
            tagger = enabled['GENIA']
            self.feat_genia = GeniaFeatures(tagger,data)

        # Only create UMLS cache if module is available
        if enabled['UMLS']:
            self.feat_umls = UMLSFeatures()



        self.enabled_IOB_prose_sentence_features = []
        #self.enabled_IOB_prose_sentence_features.append('pos')
        #self.enabled_IOB_prose_sentence_features.append('prev_3_pos')
        #self.enabled_IOB_prose_sentence_features.append('next_3_pos')
        self.enabled_IOB_prose_sentence_features.append('prev')
        #self.enabled_IOB_prose_sentence_features.append('prev2')
        #self.enabled_IOB_prose_sentence_features.append('prev3')
        self.enabled_IOB_prose_sentence_features.append('next')
        #self.enabled_IOB_prose_sentence_features.append('next2')
        #self.enabled_IOB_prose_sentence_features.append('next3')
        self.enabled_IOB_prose_sentence_features.append('GENIA')
        #self.enabled_IOB_prose_sentence_features.append('UMLS')




    # IOB_prose_features()
    #
    # input:  A sentence
    # output: A list of hash tables of features
    def IOB_prose_features(self, sentence):

        features_list = []

        # Get a feature set for each word in the sentence
        for i,word in enumerate(sentence):
            features_list.append(self.feat_word.IOB_prose_features(sentence[i]))


        # Only POS tag once
        if 'pos' in self.enabled_IOB_prose_sentence_features:
            pos_tagged = nltk.pos_tag(sentence)


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_prose_sentence_features:


            # Feature: Part of Speech
            if feature == 'pos':
                for (i,(_,pos)) in enumerate(pos_tagged):
                    features_list[i].update( { ('pos',pos) : 1} )


            # Feature: Previous 3 POSs
            if feature == 'prev_3_pos':
                for i in range(len(sentence)):
                    # Where to begin
                    if i-3 < 0:
                        begin = 0
                    else:
                        begin = i-3

                    # Go as far back as 3 tokens
                    pos_features = {}
                    for p in pos_tagged[begin:i]:
                        pos = p[1]
                        pos_features.update( {('prev_3_pos',pos) : 1} )
                    
                    # Update feature dict
                    features_list[i].update(pos_features)


            # Feature: Previous 3 POSs
            if feature == 'next_3_pos':
                for i in range(len(sentence)):
                    pos_features = {}
                    for p in pos_tagged[i:i+3]:
                        pos = p[1]
                        pos_features.update( {('next_3_pos',pos) : 1} )
                    
                    # Update feature dict
                    features_list[i].update(pos_features)


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
                for i in range(len(sentence)):
                    word = sentence[i]
                    umls_features = self.feat_umls.IOB_prose_features(word)
                    features_list[i].update( umls_features )


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

        if "prev3" in self.enabled_IOB_prose_sentence_features:
            prev3 = lambda f: {("prev3_"+k[0], k[1]): v/4.0 for k,v in f.items()}
            prev_list = map(prev3, features_list)
            for i in range(len(features_list)):
                if i < len(features_list) - 4:
                    ngram_features[i].update(prev_list[i+3])
                elif i == len(features_list) - 3:
                    ngram_features[i][("prev3", "***")] = 1
                elif i == len(features_list) - 2:
                    ngram_features[i][("prev3", "**" )] = 1
                else:
                    ngram_features[i][("prev3", "*"  )] = 1

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

        if "next3" in self.enabled_IOB_prose_sentence_features:
            next3 = lambda f: {("next3_"+k[0], k[1]): v/4.0 for k,v in f.items()}
            next_list = map(next3, features_list)
            for i in range(len(features_list)):
                if i < len(features_list) - 4:
                    ngram_features[i].update(next_list[i+3])
                elif i == len(features_list) - 3:
                    ngram_features[i][("next3", "***")] = 1
                elif i == len(features_list) - 2:
                    ngram_features[i][("next3", "**" )] = 1
                else:
                    ngram_features[i][("next3", "*"  )] = 1


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


        if 'pos' in self.enabled_IOB_nonprose_sentence_features:
            pos_tagged = nltk.pos_tag(sentence)


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_nonprose_sentence_features:

            # Feature: Part of Speech
            if feature == 'pos':
                for (i,(_,pos)) in enumerate(pos_tagged):
                    features_list[i][ ('pos',pos) ] = 1


            # Feature: Previous 3 POSs
            if feature == 'prev_3_pos':
                for i in range(len(sentence)):
                    # Where to begin
                    if i-3 < 0:
                        begin = 0
                    else:
                        begin = i-3

                    # Go as far back as 3 tokens
                    pos_features = {}
                    for p in pos_tagged[begin:i]:
                        pos = p[1]
                        pos_features.update( {('prev_3_pos',pos) : 1} )
                    
                    # Update feature dict
                    features_list[i].update(pos_features)


            # Feature: Previous 3 POSs
            if feature == 'next_3_pos':
                for i in range(len(sentence)):
                    pos_features = {}
                    for p in pos_tagged[i+1:i+4]:
                        pos = p[1]
                        pos_features.update( {('next_3_pos',pos) : 1} )
                    
                    # Update feature dict
                    features_list[i].update(pos_features)


            # Feature: UMLS Word Features (only use nonprose ones)
            if (feature == "UMLS") and enabled['UMLS']:
                for i in range(len(sentence)):
                    word = sentence[i]
                    umls_features = self.feat_umls.IOB_nonprose_features(word)
                    features_list[i].update( umls_features )

            # Feature: Test Result (for each chunk)
            if feature == "test_result":
                for index, features in enumerate(features_list):
                    right = " ".join([w for w in sentence[index:]])
                    if self.feat_word.is_test_result(right):
                        features['test_result'] = 1



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


        # FIXME - more closely resembling Harabagiu
        return features_list


        # Split the chunked sentence into a list of words for (POS tagger)
        split_sentence = []
        for c in sentence:
            split_sentence += c.split()
        tags = nltk.pos_tag(split_sentence)


        pflag = False
        if ' '.join(sentence) == 'PMH : Carpal tunnel syndrome , Hypertension , Hyperlipidemia , Arthritis':
            pflag = True
            #print '\n\n\n'
            #print 'sentence: ', sentence
            #print 'inds:     ', chunk_inds
            #print 'tags:     ', tags
            #print
            #print '\n\n'



        # Allow for particular features to be enabled
        for feature in self.enabled_concept_features:

             # Features: UMLS features
            if (feature == "UMLS") and enabled['UMLS']:
                umls_features = self.feat_umls.concept_features_for_sentence(split_sentence)
                features.update(umls_features)


            # Feature: Previous POSs
            if feature == 'pos':
                for i,ind in enumerate(chunk_inds):
                    # Find beginning index of chunk
                    split_ind = 0
                    for c in sentence[:ind]:
                        split_ind += len(c.split())
                    end_ind = split_ind + len(sentence[ind].split())

                    # All words in chunk
                    for tag in tags[split_ind:end_ind]:
                        pos = tag[1]
                        features_list[i][('pos',pos)] = 1


            # Feature: Previous 3 POSs
            if feature == 'prev_3_pos':
                for i,ind in enumerate(chunk_inds):
                    # Find beginning index of chunk
                    split_ind = 0
                    for c in sentence[:ind]:
                        split_ind += len(c.split())

                    # Three previous words
                    begin = split_ind-3  if  split_ind-3>0  else  0
                    for tag in tags[begin:split_ind]:
                        pos = tag[1]
                        features_list[i][('prev_3_pos',pos)] = 1


            continue


            # Feature: Previous Chunks's Features
            if feature == "prev":
                if ind == 0:
                    features[("prev", "*")] = 1
                else:
                    # Get features of previous chunks
                    prev_features = self.feat_sent.concept_features_for_chunk(sentence,ind-1)
                    prepend = lambda f: {("prev_"+k[0],k[1]):v for k, v in f.items()}
                    features.update( prepend(prev_features) )


            # Feature: Next Chunk's Features
            if features == "next":
                if ind == len(sentence) - 1:
                    features[("next", "*")] = 1
                else:
                    # Get features of previous chunks
                    next_features = self.feat_sent.concept_features_for_chunk(sentence,ind+1)
                    prepend = lambda f: {("next_"+k[0],k[1]):v for k, v in f.items()}
                    features.update( prepend(next_features) )




            # Feature: Wordnet Stem (for each chunk)
            if feature == "stem_wordnet":
                morphy_tags = {
                    'NN': nltk.corpus.reader.wordnet.NOUN,
                    'JJ': nltk.corpus.reader.wordnet.ADJ,
                    'VB': nltk.corpus.reader.wordnet.VERB,
                    'RB': nltk.corpus.reader.wordnet.ADV}
                morphy_tags = [(w, morphy_tags.setdefault(t[:2], nltk.corpus.reader.wordnet.NOUN)) for w, t in tags]
                st = nltk.stem.WordNetLemmatizer()
                tag = morphy_tags[ind]
                # FIXME
                #features[(feature, st.lemmatize(*tag))] = 1


            # Feature: Test Result (for each chunk)
            if feature == "test_result":
                # FIXME
                right = " ".join([c for c in sentence[ind:]])
                if self.feat_word.is_test_result(right):
                    features[(feature, None)] = 1


        #if pflag:
        #    for f in features_list:
        #        print sorted(f.items())
        #        print 


        return features_list


