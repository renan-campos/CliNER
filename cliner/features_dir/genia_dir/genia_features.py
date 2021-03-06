######################################################################
#  CliCon - genia_features.py                                        #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Independent GENIA module                                 #
######################################################################



import interface_genia
from features_dir import utilities


class GeniaFeatures:


    def __init__(self, tagger, data):

        """
        Constructor.

        @param data. A list of split sentences
        """

        # Filter out nonprose sentences
        prose = [ sent  for  sent  in  data  if  utilities.is_prose_sentence(sent) ]

        # Process prose sentences with GENIA tagger
        self.GENIA_features = iter(interface_genia.genia(tagger, prose))




    def features(self, sentence, is_prose=True):

        """
        features()

        @param sentence. A list of words to bind features to
        @param is_prose. Mechanism for skipping nonprose (for alignment)
        @return          list of dictionaries (of features)

        Note: All data is tagged upon instantiation of GeniaFeatures object.
              This function MUST take each line of the file (in order) as input
        """

        # Return value is a list of dictionaries (of features)
        features_list = [ {}  for  _  in  sentence ]


        # Mechanism to allow for skipping nonprose
        if not is_prose: return []


        # Get the GENIA features of the current sentence
        genia_feats = next( self.GENIA_features )


        # Feature: Current word's GENIA features
        for i,curr in enumerate(genia_feats):
            keys = ['GENIA-stem','GENIA-POS','GENIA-chunktag']
            #keys = ['GENIA-stem','GENIA-POS','GENIA-chunktag', 'GENIA-NEtag']
            output = dict( ((k, curr[k]), 1) for k in keys if k in curr )
            features_list[i].update(output)


        return features_list

