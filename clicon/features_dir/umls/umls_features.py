######################################################################
#  CliCon - umls_features.py                                         #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Independent UMLS module                                  #
######################################################################



from sets import ImmutableSet
from umls_cache import UmlsCache
import umls



class UMLSFeatures:


    enabled_prose_features    = ImmutableSet( [ 'umls_cui', 'umls_semantic_type_word', 'umls_hypernyms' ] )

    enabled_nonprose_features = ImmutableSet( [ 'umls_cui', 'umls_semantic_type_word' ] )


    enabled_concept_features_for_word = ImmutableSet( [ 'umls_semantic_type_word', 'umls_cui' ] )
    enabled_concept_features_for_sentence = ImmutableSet( [ 'umls_semantic_type_sentence', 'umls_semantic_context' ] )



    def __init__(self):

        """
        UMLSFeatures::Constructor
        """

        # cache for the mappings of all umls lookups made
        self.umls_lookup_cache = UmlsCache()




    def IOB_prose_features(self, word):

        """
        UMLSFeatures::IOB_prose_features()

        @ param word.  word to lookup in UMLS database
        @return        dictionary of features
        """

        # Return value is a list of dictionaries (of features)
        features = {}


        for feature in self.enabled_prose_features:


            # Feature: UMLS Semantic Types
            if feature == "umls_cui":

                # Get UMLS CUIs (could have multiple)
                cuis = umls.get_cui(self.umls_lookup_cache , word)

                # Add each CUI
                if cuis:
                    for cui in cuis:
                        features[(feature,cui)] = 1


            # Feature: UMLS Hypernyms
            if feature == "umls_hypernyms":

                # Get UMLS hypernyms
                hyps = umls.umls_hypernyms(self.umls_lookup_cache,word)

                # Add all hypernyms
                if hyps:
                    #for hyp in hyps:
                    features[(feature,hyps[0])] = 1


            # Feature: UMLS Semantic Type (for each word)
            if feature == "umls_semantic_type_word":
                # Get UMLS semantic type (could have multiple)
                mapping = umls.umls_semantic_type_word(self.umls_lookup_cache , word )

                #print mapping

                # If is at least one semantic type
                if mapping != None:
                    for concept in mapping:
                        features[('umls_semantic_type_word', concept )] = 1


        return features



    def IOB_nonprose_features(self, word):

        """
        UMLSFeatures::IOB_nonprose_features()

        @ param word.  word to lookup in UMLS database
        @return        dictionary of features
        """

        # Return value is a list of dictionaries (of features)
        features = {}


        for feature in self.enabled_nonprose_features:


            # Feature: UMLS Semantic Types
            if feature == "umls_cui":
                # Get UMLS CUIs (could have multiple)
                cuis = umls.get_cui(self.umls_lookup_cache , word)

                # Add each CUI
                for cui in cuis:
                    features[(feature,cui)] = 1


            # Feature: UMLS Semantic Type (for each word)
            if feature == "umls_semantic_type_word":
                # Get UMLS semantic type (could have multiple)
                mapping = umls.umls_semantic_type_word(self.umls_lookup_cache , word )
                # If is at least one semantic type
                if mapping != None:
                    for concept in mapping:
                        features[('umls_semantic_type_word', concept )] = 1


        return features




    def concept_features_for_word(self, word):

        """
        UMLSFeatures::concept_features_for_word()

        @ param word.  word to lookup in UMLS database
        @return        dictionary of  word-level features
        """


        # Return value is a list of dictionaries (of features)
        features = {}


        for feature in self.enabled_concept_features_for_word:

            # Feature: UMLS Semantic Types
            if feature == "umls_cui":

                # Get UMLS CUIs (could have multiple)
                cuis = umls.get_cui(self.umls_lookup_cache , word)

                # Add each CUI
                if cuis:
                    for cui in cuis:
                        features[(feature,cui)] = 1


            # Feature: UMLS Semantic Type (for each word)
            if feature == "umls_semantic_type_word":

                # Get UMLS semantic type (could have multiple)
                mapping = umls.umls_semantic_type_word(self.umls_lookup_cache , word )
                # If is at least one semantic type
                if mapping:
                    for concept in mapping:
                        features[('umls_semantic_type_word', concept )] = 1


        return features



    def concept_features_for_sentence(self, sentence):

        """
        UMLSFeatures::concept_features_for_sentence()

        @ param sentence. list of words from line (after flattening chunks)
        @return           dictionary of chunk-level features
        """


        # Return value is a list of dictionaries (of features)
        features = {}


        for feature in self.enabled_concept_features_for_sentence:


            # Feature: UMLS semantic type for the sentence
            if feature == "umls_semantic_type_sentence":

                # a list of the uml semantic of the largest substring(s).
                sentence_mapping = umls.umls_semantic_type_sentence( self.umls_lookup_cache, sentence )

                # if there are no mappings
                if not sentence_mapping:
                    features[('umls_semantic_type_sentence', None ) ] = 1
                # assign the umls definitions to the vector for each word
                else:

                    for concept in sentence_mapping:
                        if concept:
                            for mapping in concept:
                                features[('umls_semantic_type_sentence' , mapping[0] ) ] = 1


            # Feature: UMLS semantic context
            if feature == "umls_semantic_context":

                # the umls definition of the largest string the word is in
                umls_semantic_context_mappings = umls.umls_semantic_context_of_words( self.umls_lookup_cache , sentence )

                # there could be multiple contexts, iterate through the sublist
                for mapping in umls_semantic_context_mappings:
                    if not mapping: continue
                    for concept in mapping:
                        features[(feature,concept)] = 1


        return features
