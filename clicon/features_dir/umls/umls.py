import cPickle as pickle
import SQLookup 

def umls_semantic_type_word( umls_string_cache , sentence ):

    #If the umls semantic type is in the cache use that semantic type otherwise lookup the semantic type and add to the cache.
    if umls_string_cache.has_key( sentence ):
        mapping = umls_string_cache.get_map( sentence )
    else:
        concept = SQLookup.string_lookup( sentence )
        umls_string_cache.add_map( sentence , concept )
        '''
        if concept != None:
            #umls_string_cache.add_map( sentence , concept[0] )
            umls_string_cache.add_map( sentence , concept )
        else:
            umls_string_cache.add_map( sentence , None )
        '''
        mapping = umls_string_cache.get_map(sentence)

    #print 'umls_semantic_type_word - returning:'
    #print mapping
    #print ''

    return mapping  
    

def umls_semantic_context_of_words( umls_string_cache, sentence ):
     
    #Defines the largest string span for the sentence.
    WINDOW_SIZE = 7

    #Holds the span of the umls concept of the largest substring that each word in sentence is found in.
    umls_context_list = []

    #Holds the span of the concept for each substring. 
    #A tuple containing tne beginning and end index of a substring functions as the key and the key is assigned to a umls definition. 
    concept_span_dict = {} 

    #Initialize the umls_context_list with empty lists. Each sublist functions as the mappings for each word. 
    for i in sentence: 
        umls_context_list.append( [] )
 
    #Creates and finds the span of a umls concept for each possible substring of length 1 to currentWindowSize. 
    for currentWindowSize in range( 1 , WINDOW_SIZE ):
        for ti in range( 0 , ( len(sentence) - currentWindowSize ) + 1 ): 
            rawstring = "" 
            for tj in range( ti , ti + currentWindowSize): 
                rawstring += ( sentence[tj] + " " ) 
            
            #Each string is of length 1 to currentWindowSize.
            rawstring = rawstring[0:-1]  

            #If the string is not in cache, look the umls concept up and add to the cache. 
            if not( umls_string_cache.has_key( rawstring ) ):
                #SQLookup returns a tuple if there is a result or None is there is not.  
                concept = SQLookup.string_lookup( rawstring )
                
#                print concept 
    
                if not concept:
                    umls_string_cache.add_map( rawstring, None ) 
                else:
                    umls_string_cache.add_map( rawstring, concept ) ; 
            
#                if concept != None:
 #                   umls_string_cache.add_map( rawstring , concept[0] )
  #              else:
   #                 umls_string_cache.add_map( rawstring , None ) 

            #Store the concept into concept_span_dict with its span as a key.
            concept_span_dict[(ti,ti+currentWindowSize-1)] = umls_string_cache.get_map( rawstring )

            #For each substring of the sentence if there is a definition obtained from 
            #SQLookup assign the concept to every word that is within in the substring.
            #If the currrent span is a substring update otherwise if it is not a substring add the new found context. 
            if umls_string_cache.get_map(rawstring):

                for i in range( ti , ti + currentWindowSize ):  
                    
                    if len( umls_context_list[i] ) == 0:
                        umls_context_list[i].append( [ ti , ti + currentWindowSize - 1 ] )
     
                    else: 
                        updated = 0 
                        for j in umls_context_list[i]:
                            if j[0] >= ti and j[1] <= ( ti + currentWindowSize - 1 ):
                                j[0] = ti
                                j[1] = ( ti + currentWindowSize - 1 ) 
                                updated += 1
                        if not(updated):
                            if umls_context_list[i].count( [ti,ti+currentWindowSize -1] ) == 0 :
                                umls_context_list[i].append( [ ti , ti +currentWindowSize - 1 ] ) 
    

    #print '\t\t', umls_context_list

    #create a list of sublists 
    #  each sublist represents the contexts for which the word appears in the sentence

 #   print umls_context_list 

    mappings = [] 
    for i in umls_context_list:
        spans = i 
        if len(spans) == 0:
            mappings.append( None ) 
        else:
            sub_mappings = []
            for j in spans:
                sub_mappings.append( concept_span_dict[tuple(j)])

            # FIXME - Decided to concat rather than append (not sure why)
            mappings += sub_mappings 

    return mappings 


def umls_semantic_type_sentence( cache , sentence ):

    #print sentence

    #Defines the largest string span for the sentence.                                                                                               

    WINDOW_SIZE = 7

    #holds the mappings for every substring of size 1 to WINDOW_SIZE             
    mappings = {}
 
    #Creates and finds the span of a umls concept for each possible substring of length 1 to currentWindowSize.                                                                                                   
    for currentWindowSize in range( 1 , WINDOW_SIZE ):
        for ti in range( 0 , ( len(sentence) - currentWindowSize ) + 1 ):

            rawstring = ""

            for tj in range( ti , ti + currentWindowSize):
                rawstring += ( sentence[tj] + " " )

            #Each string is of length 1 to currentWindowSize.                                                                                                                                  
            rawstring = rawstring[0:-1]

            #If the umls semantic type is already in the cache then us the one stored otherwise lookup and add to cache 
            if cache.has_key( rawstring ):
                mappings[rawstring] = cache.get_map( rawstring )

            else:

                concept = string_lookup( rawstring )

                #cache.add_map( rawstring , concept )

                if concept:
                    cache.add_map( rawstring , concept )
                else:
                    cache.add_map( rawstring  , [] )

                mappings[rawstring] = cache.get_map( rawstring )
#            print "rawstring: ", rawstring
 #           print "mappings: " ,mappings[rawstring] 
    size_s = 0

    phrase = []

    
    #print "mappings: " , mappings 
    #get longest sub string with a mapping 

    for mapping in mappings.iteritems():
        #print mapping 
        if(  mapping[1]  ):
 #           print mapping 
            if( len( mapping[0] )   > size_s ):

                phrase = []
                phrase.append( mapping[1] )
                size_s = len( mapping[0] )
                continue
            if( len(mapping[0]) == size_s ):
                phrase.append( mapping[1] )
  
#    print "phrase: " , phrase
#    print phrase 
    return phrase



# Get the semantic types for a given word
def get_cui( cache , word ):

    # If hypernyms already in cache
    if cache.has_key( word + '--cuis' ):

        cuis = cache.get_map( word + '--cuis' )

    else:

        # Get cui
        cuis = SQLookup.cui_lookup(word)

        # Eliminate duplicates
        cuis = list(set(cuis))
        cuis = [c[0] for c in cuis]

        # Store result in cache
        cache.add_map( word + '--cuis', cuis )

    return cuis



# Get the hypernyms of a string
def umls_hypernyms( cache, string ):

    #print 'hypernym lookup is unacceptably slow'
    return []

    # If hypernyms already in cache
    if cache.has_key( string + '--hypernyms' ):

        hyps = cache.get_map( string + '--hypernyms' )

    else:

        # Get hypernyms
        hyps = SQLookup.hypernyms_lookup(string)

        # Store result in cache
        cache.add_map( string + '--hypernyms' , hyps )

    return hyps

