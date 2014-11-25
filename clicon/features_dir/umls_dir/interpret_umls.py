import os
import sys
import cPickle as pickle
import interface_umls

sys.path.append((os.environ["CLICON_DIR"] + "/clicon/normalization/lvg"))
sys.path.append((os.environ["CLICON_DIR"] + "/clicon/normalization/spellCheck"))
sys.path.append((os.environ["CLICON_DIR"] + "/clicon/features_dir/cuiLookup"))

from lvgNorm import lvgNormalize
from spellChecker import spellCheck
from cuiLookup import getConceptId

def umls_semantic_type_word( umls_string_cache , sentence ):
    # Already cached?
    if False and umls_string_cache.has_key( sentence ):
        mapping = umls_string_cache.get_map( sentence )
    else:
        concepts = interface_umls.string_lookup( sentence )
        concepts = [  singleton[0]  for singleton  in set(concepts)  ]
        umls_string_cache.add_map(sentence , concepts)
        mapping = umls_string_cache.get_map(sentence)

    return mapping
    

def umls_semantic_context_of_words( umls_string_cache, sentence ):
     
    #Defines the largest string span for the sentence.
    WINDOW_SIZE = 7

    # span of the umls concept of the largest substring
    umls_context_list = []

    # keys: tuple of (start,end) index of a substring
    concept_span_dict = {} 

    # Each sublist functions as the mappings for each word. 
    for i in sentence: 
        umls_context_list.append( [] )
 
    # finds the span for each substring of length 1 to currentWindowSize. 
    for currentWindowSize in range( 1 , WINDOW_SIZE ):
        for ti in range( 0 , ( len(sentence) - currentWindowSize ) + 1 ): 
            rawstring = "" 
            for tj in range( ti , ti + currentWindowSize): 
                rawstring += ( sentence[tj] + " " ) 
            
            #Each string is of length 1 to currentWindowSize.
            rawstring = rawstring.strip()

            # Not in cache yet?
            if not( umls_string_cache.has_key( rawstring ) ):
                # returns a tuple if there is a result or None is there is not.  
                concept = interface_umls.string_lookup( rawstring )
                
                if not concept:
                    umls_string_cache.add_map( rawstring, None ) 
                else:
                    umls_string_cache.add_map( rawstring, concept ) ; 
            
            #Store the concept into concept_span_dict with its span as a key.
            concept_span_dict[(ti,ti+currentWindowSize-1)] = umls_string_cache.get_map( rawstring )

            # For each substring if there is a span, then
            #   assign the concept to every word that is within in the substring
            if umls_string_cache.get_map(rawstring):
                for i in range( ti , ti + currentWindowSize ):  
                    if len( umls_context_list[i] ) == 0:
                        umls_context_list[i].append([ti,ti+currentWindowSize-1])
     
                    else: 
                        updated = 0 
                        for j in umls_context_list[i]:
                            if j[0] >= ti and j[1] <= (ti+currentWindowSize-1):
                                j[0] = ti
                                j[1] = ( ti + currentWindowSize - 1 ) 
                                updated += 1
                        if not(updated):
                            val = [ti,ti+currentWindowSize-1]
                            if umls_context_list[i].count(val)== 0:
                                umls_context_list[i].append(val) 
    


    #create a list of sublists 
    #  each sublist represents the contexts for which the word appears
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

    #Defines the largest string span for the sentence.
    WINDOW_SIZE = 7

    longestSpanLength = 0
    longestSpans = []       # List of (start,end) tokens

    for i in range(len(sentence)):
        maxVal = min(i+WINDOW_SIZE, len(sentence))
        for j in range(i,maxVal):
            # Lookup key
            span = sentence[i:j+1]
            rawstring = unicode(' '.join(span))

            # string does have an associated UMLS concept?
            if interface_umls.concept_exists(rawstring):
                if   len(span) == longestSpanLength:
                    longestSpans.append( (i,j) )
                # new longest span size
                elif len(span) >  longestSpanLength:
                    longestSpans = [ (i,j) ]
                    longestSpanLength = len(span)

    # lookup UMLS concept for a given (start,end) span
    def span2concept(span):
        rawstring = ' '.join(sentence[span[0]:span[1]+1])

        # Already cached?
        if cache.has_key( rawstring ):
            return cache.get_map( rawstring )

        else:
            concept = interface_umls.string_lookup( rawstring )

            if concept:
                cache.add_map( rawstring , concept )
            else:
                cache.add_map( rawstring  , [] )

            return cache.get_map( rawstring )

    mappings = [ span2concept(span) for span in longestSpans ]
    return mappings

def abr_lookup( cache, word):
    """ get expansions of an abbreviation """
    if cache.has_key( word + "--abrs"):
        abbreviations = cache.get_map( word + "--abrs")
    else:
        abbreviations = interface_umls.abr_lookup(word)

        if abbreviations != []:

            # the lookup returns a list of tuples so now it will be converted to a list of strings
            abbreviations =  [tuple[0] for tuple in abbreviations]

        cache.add_map( word + "--abrs", abbreviations)
    return abbreviations

def get_cuis_for_abr(cache, word):
    """ gets cui for each possible expansion of abbreviation """
    if cache.has_key( word + "--cuis_of_abr"):
        cuis_of_abr = cache.get_map( word + "--cuis_of_abr" )
    else:
        cuis_of_abr = {}
        for phrase in abr_lookup(cache, word):
            cuis_of_abr[phrase] = get_cui(cache, phrase)

        cache.add_map( word + "cuis_of_abr", cuis_of_abr )

    return cuis_of_abr

def get_tui( cache, cuiStr ):
    """ get tui of a cui """
    if cache.has_key( cuiStr ):
        tui = cache.get_map( cuiStr )
    else:
        # list of singleton tuples
        tui = interface_umls.tui_lookup(cuiStr)

        # change to list of strings
        tui = [semanticType[0] for semanticType in tui]

        cache.add_map(cuiStr, tui)

    return tui

# Get the umls concept id for a given word
def get_cui( cache , word ):

    # If already in cache
    if cache.has_key( word + '--cuis' ):

        cuis = cache.get_map( word + '--cuis' )

    else:

        # Get cui
        cuis = interface_umls.cui_lookup(word)

        # Eliminate duplicates
        cuis = list(set(cuis))
        cuis = [c[0] for c in cuis]

        # Store result in cache
        cache.add_map( word + '--cuis', cuis )

    return cuis

def get_list_all_possible_cuis_for_abrv(cache, phrase):
    """
    get cuis for every possible possible abbreviation expansion.

    To define your own filter go to:

    page 3:

    http://semanticnetwork.nlm.nih.gov/SemGroups/Papers/2003-medinfo-atm.pdf

    look up categories and semantic types and get the tui from:

    http://metamap.nlm.nih.gov/Docs/SemanticTypes_2013AA.txt

    """

    phrases = get_cuis_for_abr(cache, phrase)

    results = set()

    # change fromdictionary to a set of strings.
    for phrase in phrases:
        for cui in phrases[phrase]:
            results.add(cui)

    return list(results)


def get_most_freq_cui(cui_list):
    """
    from a list of strings get the cui string that appears the most frequently.

    Note: if there is no frequency stored then this will crash.
    """

    cui_freq = pickle.load( open( os.getenv('CLICON_DIR' ) + "/cui_freq/cui_freq", "rb" ) )

    cui_highest_freq = None

    for cui in cui_list:

        if cui in cui_freq:

            # sets an initial cui
            if cui_highest_freq is None:
                cui_highest_freq = cui

            # assign new highest
            elif cui_freq[cui] > cui_freq[cui_highest_freq]:
                cui_highest_freq = cui   

    # at this point we have not found any concept ids with a frequency greater than 0.
    # good chance it is CUI-less
    if cui_highest_freq is None:
        cui_highest_freq = "CUI-less"

    return cui_highest_freq

def filter_cuis_by_tui(cache, cuis, filter=["T020", # acquired abnormality
                                         "T190", # Anatomical Abnormality
                                         "T049", # Cell or Molecular Dysfunction
                                         "T019", # Congenital Abnormality
                                         "T047", # Disease or Syndrome
                                         "T050", # Experimental Model of Disease
                                         "T033", # Finding
                                         "T037", # Injury or Poisoning
                                         "T048", # Mental or Behavioral Dysfunction
                                         "T191", # Neoplastic Process
                                         "T046", # Pathologic Function
                                         "T184"]):
    """ removes cuis that do not have tui that is in the filter """
    results = set()

    for cui in cuis:
        for tui in get_tui(cache, cui):
            if tui in filter:
                results.add(cui)
                break

    return list(results)

def obtain_concept_id(cache, phrase, filter):
    """
    perform a concept id lookup for a phrase of a certain tui
    """

    cuis = set()

    # NOTE: gotConceptId is very time consuming
    # sets are not indexable so convert for indexing.
    # getConceptId returns dictionary of the form {"text":"text argument", "concept_ids":Set([..])}
    conceptIds = getConceptId(phrase)["concept_ids"]

    if conceptIds is not None:
        cuis = cuis.union(filter_cuis_by_tui(cache, list(conceptIds), filter=filter))

    conceptId = get_most_freq_cui(list(cuis))

    if conceptId == "CUI-less":

        cuis = set()

        normPhrases = []

        # normalize with lvg
        #normPhrases = lvgNormalize(phrase)

        norm = ""
        for char in phrase:
            if char.isalnum() is True or char.isspace() is True:
                norm += char

        # in some cases CASE does matter for abbreviations
        normPhrases.append( norm )

        for normPhrase in normPhrases:

            # get expansions of abbreviations and search for their cuis
            if len(normPhrase) < 4:
                cuisForAbr = get_list_all_possible_cuis_for_abrv(cache, normPhrase)
                cuisForAbr = filter_cuis_by_tui(cache, cuisForAbr, filter=filter)
                cuis = cuis.union(cuisForAbr)

            # if phrase is longer than 3 chars then it is probably not an abbreviation.
            else:
                conceptIds = get_cui(cache, normPhrase)
                conceptIds = filter_cuis_by_tui(cache, conceptIds, filter=filter)
                cuis = cuis.union(conceptIds)

        # get most frequent cui
        if len(cuis) != 0:
            conceptId = get_most_freq_cui(list(cuis))
        else:
            conceptId = "CUI-less"

        # perform spell checking and attempt search for cui one last time.
        if conceptId == "CUI-less":

            cuis = set()

            phrase = spellCheck(phrase)

            conceptIds = getConceptId(phrase)["concept_ids"]

            if conceptIds is not None:
                cuis = cuis.union(filter_cuis_by_tui(cache, list(conceptIds), filter=filter))

            conceptId = get_most_freq_cui(list(cuis))

    return conceptId

#EOF

