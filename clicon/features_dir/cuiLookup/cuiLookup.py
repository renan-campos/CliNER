import subprocess
import re
import os
import imp
import sys

#sys.path.append((os.environ["CLICON_DIR"] + "/clicon/features_dir/umls_dir"))

#from umls_cache import UmlsCache

def getConceptId(cache, phrase):
    """
    performs a cui lookup on a phrase using metamap java api.
    """

    baseDirPath = os.environ["CLICON_DIR"]

    if baseDirPath is None:
       raise Exception("CLICON_DIR not defined")

    os.chdir(baseDirPath + "/clicon/features_dir/cuiLookup")

    metaMapApiJarPath  = ":metamapBase/public_mm/src/javaapi/dist/MetaMapApi.jar"
    prologBeansJarPath = ":metamapBase/public_mm/src/javaapi/dist/prologbeans.jar"

    # jar paths used for -cp. used to linked dependencies to program
    cpArgs =  ".{0}{1}".format(metaMapApiJarPath,
                              prologBeansJarPath)
    # the compiled java program to execute
    progArg = "gov.nih.nlm.nls.metamap.cuiLookup"

    if cache.has_key(phrase + "--metamap"):

  #      print "HAS MAPPING!: ", phrase
        result = cache.get_map(phrase + "--metamap")
    else:

 #       print "NO MAPPING!: ", phrase

        # get resulting output of lookup
        stdout = subprocess.check_output(["java", "-cp", cpArgs, progArg, phrase])

        # dictionary
        result = extractConceptIdsFromStdout(stdout)

        cache.add_map(phrase + "--metamap", result)

#    print "RESULTS: ", result
    return result

def extractConceptIdsFromStdout(stdout):
    """
    processes output produced from java program cuiLookup

    and returns a dictionary of phrases mapped to a set of concept id's

    a phrase will be mapped to None if there are no concept id's
    """

    results = {}

    for line in stdout.split('\n'):

        if lineIsPhrase(line):

            phrase =  extractPhrase(line)

            # if line is a phrase output then create new if in not already existing
            if phrase not in results:

                results["concept_ids"] = None

                results["text"] = phrase

        if lineIsConceptId(line):
        
            cui = extractCui(line)

            if cui is None:
                
                # if there is no concept id then do nothing.
                pass

            elif results["concept_ids"] is None:

                # if there is a concept id but nothing is already assigned to the phrase then assign a list.
                results["concept_ids"] = set()

                results["concept_ids"].add(cui)

            else:
       
                # if a list is already assigned then append to concept id list.
                results["concept_ids"].add(cui)

    print results
    return results

def lineIsPhrase(lineFromStdout):
    return ("phrase: " in lineFromStdout)

def lineIsConceptId(lineFromStdout):
    return ("concept id: " in lineFromStdout)

def extractPhrase(lineFromStdout):
    return re.sub("phrase: ", '', lineFromStdout)

def extractCui(lineFromStdout):
    cui = re.sub("concept id: ", '', lineFromStdout)

    if cui == "None":
        cui = None

    return cui

if __name__ == "__main__":
    
    print "Input phrase: "
    phrase = input()

    print getConceptId(phrase)
    #print cuiLookup("blood")
    #print cuiLookup("the man went down to georgia")
