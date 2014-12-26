from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Process

import sys
import re
import copy
import os
import time
from sets import Set

#TODO: there are some extreme circumstances that may cause this to not work.

def writeToFile(path, string):
    """
    writes to file as the bash script needs input from a file.
    """

    filePath = path+"/stanfordStrArg.txt"
    file = open(filePath, "w")
    file.write(string)
    file.close()
    return filePath

def getParserDir():
    """
    reads config file and returns the dir of lexical parser.
    config file should contain absolute path of standford nlp parser dir.
    """

    configFile = open(os.environ["CLICON_DIR"] + "/clicon/features_dir/stanfordNLP/parser_path_config.txt")

    configSettings = configFile.read().strip("\n")

    dirPath = re.sub("PARSER_PATH=", "", configSettings)

    if dirPath == "None":
        dirPath = None

    return dirPath

def parseString(string):
    """
    obtains all collapsed dependencies that can be used to create a tree for generating dependency paths.
    the output of the parser is returned which is a string.
    """

    dirPath = getParserDir()

    if dirPath is None:
        print "Need to put in the directory of the lexicalized parser in order to use this module"
        exit()

    filePath = writeToFile(dirPath, string)

    dependencyCmd = ["java",
               "-mx2100m",
               "-cp", dirPath+"/*:",
               "edu.stanford.nlp.parser.lexparser.LexicalizedParser",
               "-sentences", 
               "newline",
               "-outputFormatOptions",
               "treeDependencies",
               "-retainTmpSubcategories",
               "-outputFormat",
               "typedDependencies",
               "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz",
               filePath]
 
    process = Popen(dependencyCmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)

    retVal = process.communicate()[0]

    return retVal

def getCollapsedDepdencies(string):
    """
    returns a list of list of dictionaries

    of form:  [[{"span":("tok1", "tok2"), "rel":"rel_type__relation"},...]...]
    """

    outputFromParser = parseString(string)

    print outputFromParser

    exit()

    dependencyGroups = getDependencyGroups(outputFromParser)

    collapsedDependencyGroups = []    
    retDicts = []

    # process list of list of strings for easier handling
    for group in dependencyGroups:

        collapsedDependencies = []

        for dependency in group:

            retDict = {}

            desiredEndOfStr = dependency.find('(')
            startOfDesiredStr = desiredEndOfStr

            spans = dependency[startOfDesiredStr:]

            spans = spans[1:-1]
            spans = spans.split(', ')
            spans = tuple(spans)

            retDict["span"] = spans
            retDict["rel"]  = dependency[:desiredEndOfStr] + "__relation"

            collapsedDependencies.append(retDict)

        collapsedDependencyGroups.append(collapsedDependencies)

    return collapsedDependencyGroups

def createDependencyPaths(groupOfCollapsedDependencies):
    """ generates a hierarchy of dictionaries represent dependency tree """

    paths = []
    master = []
    tmpNodes = []

    # has immediate dependencies to root removed.
    tmpDependencies = []

    # names of nodes that are not the child dependency of any token
    rootNames = []

    # determine which phrase in the sentence is the root of the dependencies in this group.
    rootName = getRootNodeName(groupOfCollapsedDependencies)
    rootNames.append( rootName )
    rootNames += getIsolatedNodeNames(rootName, groupOfCollapsedDependencies)

    # create root nodes
    createRootNodes(rootNames, groupOfCollapsedDependencies, master)

    # gather dependencies that do not have the root token.
    for dependency in groupOfCollapsedDependencies:

        if dependency["span"][0] not in rootNames + ["ROOT-0"]:
            tmpDependencies.append(dependency)

    # creat nodes for tokens that are not root but are the parents for child dependencies
    createTmpNodes(tmpDependencies, tmpNodes)

    while len(tmpNodes) != 0:

        toRemove = []

        for dictionary in master:

            for tmpNode in tmpNodes:

                key = tmpNode.keys()[0]

                if hasKey(key, dictionary):
                   addDictToDict(key, dictionary, tmpNode[key])
                   toRemove.append( tmpNode )

        for tmpNode in toRemove:
            tmpNodes.remove(tmpNode)

    return master

def createTmpNodes(tmpDependencies, tmpNodes):
    """ used for creating dependency tree """

    for dependency in tmpDependencies:

        node = {dependency["span"][0]:{ dependency["rel"]: { dependency["span"][1]: {} } } }

        tmpNodes.append( node )

def createRootNodes(rootNames, collapsedDependencies, master):
    """ used for creating dependency tree """

    for dependency in collapsedDependencies:
    #    print dependency
        if dependency["span"][0] in rootNames:

            master.append( { dependency["span"][0]:
                               { dependency["rel"]:
                                   { dependency["span"][1]: 
                                       {} } } } )

def getIsolatedNodeNames(rootName, collapsedDependencies):
    """ 
    stanford parser generates some tokens that are not the children or anything

    this function obtains the names of those tokens.
    """

    isolatedTokens = Set()

    tokens = Set()

    for dependency in collapsedDependencies:

        if dependency["span"][0] not in [rootName, "ROOT-0"]:

            tokens.add(dependency["span"][0])

    while len(tokens) > 0:

        token = list( tokens )[0]

        isNotChild = True

        for dependency in collapsedDependencies:

            # if true then this means the dependency is the child of another token in dependency tree.
            if token == dependency["span"][1]:
                isNotChild = False

        if isNotChild is True:
            isolatedTokens.add(token)

        tokens.remove(token)

    return list(isolatedTokens)

def getRootNodeName(collapsedDependencies):
    """ determines which token is the determined to be the root."""

    for dependency in collapsedDependencies:

        if dependency["rel"] == "root__relation":

            return dependency["span"][1]

def addDependency(paths, dependency):
    """ adds a dependency to the dependency paths """

    rel = dependency["rel"]

    parent = dependency["span"][0]

    child = dependency["span"][1]

    path = { rel: { child: None } }

    addDictToDict(parent, paths, path)  

def addDictToDict(key,  parentDict, childDict):
    """ maps a child childDict to a key within a parentDict """

    if key in parentDict:

        if parentDict[key] is None:          
            parentDict[key] = copy.deepcopy(childDict)

        else:

            # if parentDict already assigned to key. do not overwrite what is there.
            childDictKey = childDict.keys()[0]

            if childDictKey in parentDict[key].keys():
                parentDict[key][childDictKey].update(copy.deepcopy(childDict)[childDictKey])
            else:
                parentDict[key].update(copy.deepcopy(childDict))

        return

    else:

        for key1 in parentDict:
            if type(parentDict[key1]) is dict:
                addDictToDict(key, parentDict[key1], childDict)

def hasKey(key, parentDict, followingPath=False):
    """ recursively determines if a key is in a hierarchy dictionary """

    result = False

    # TODO: could be a potential problem for larger sentences.
    if followingPath is True:
        keys = [stripTokes(keyInDict) for keyInDict in parentDict.keys()]

        for tok in keys:
            if tok in key:
                result = True
#                return result

    else:
        if key in parentDict:
            result = True
#            return result

    for key1 in parentDict:

        if type(parentDict[key1]) is dict:
            result = result or hasKey(key, parentDict[key1], followingPath=followingPath)

    return result

def stripTokes(string):
    # example: hello-4 -> hello, bingo-43 -> bingo, re-3d -> re-3d
    return re.sub(r"\-[0-9]+\Z", "", string)


def getDependencyGroups(outputFromParser):
    """
    processes output from stanford lexical parser.

    creates a list of list of strings
    """

    dependencyGroup = []

    grouping = []

    canAppend = False

    for line in outputFromParser.split('\n'):

         # blank line signifies a new grouping
         if len(line) == 0:

             # if canAppend is true then append the grouping to a list
             if canAppend is True:

                 dependencyGroup.append(grouping)

                 grouping = []

             # wait for the next line that is not of len 0.
             canAppend = False

         else:

             # append to a grouping
             grouping.append(line)

             canAppend = True

    return dependencyGroup

def followDependencyPath(start, end, groupsOfPaths):
    """ generates the ordered dependencies generated by createDependencyPaths """

   #print start, end

    pathsFound = []

    for groupOfPaths in groupsOfPaths:

        for path in groupOfPaths:

#            print path

            if hasKey(start, path, followingPath=True) and hasKey(end, path, followingPath=True):

                pathsFound.append( path )

#    print "PATHSZZZZ:",pathsFound

    lOflOfTokens = []

    for pathFound in pathsFound:

        for toke in [start, end]:

            indices = Set()

            tokens = getTokensInPath(toke, pathFound, tokens=[])

            tokens = [stripTokes(token) for token in tokens]

      #      print tokens

            for token in tokens:
                if token in start:
                    indices.add(tokens.index(token))
                    break

            for token in tokens:
                if token in end:
                    indices.add(tokens.index(token))
                    break


    #        print start, end
    #        print indices

            indices = list(indices)
            if len(indices) == 2:

                indices = (indices[0], indices[1]) if indices[0] < indices[1] else (indices[1], indices[0])

                tokens = tokens[indices[0]:indices[1]+1]

     #           print "TOKES:",tokens

                lOflOfTokens.append(tokens)

    return lOflOfTokens

def getTokensInPath(key, parentDict, tokens):
    """ gets all of the keys leading up to the final key in a hierarchy of dictionaries """

    for k in [stripTokes(keyInDict) for keyInDict in parentDict]:

        if k in key:

            tokens.append(k)

            return tokens

    for key1 in parentDict:

        if hasKey(key, parentDict[key1], followingPath=True):

            tokens.append(key1)

            if type(parentDict[key1]) is dict:
                
                getTokensInPath(key, parentDict[key1], tokens)

            break

    return tokens


def getDepenPathFromGroupOfDependencies(groupsOfDependencies):
    """
    obtains a list of list of dictionaies.

    ex: [[{'G': {'dep__relation': {'purulent': {'acomp__relation': {'drainage': {}}, ....]...]

    each sublist is a dependency tree. Each sublist may have multiple dictionaries where the first key is the root node.
    in this example 'G' is the root node for the dependency group.
    """

    listOfPaths = []

    # iterate over each list of dictionaries with the list of list of dictionaries
    for groupOfDependencies in groupsOfDependencies:

        #print "GROUP:", groupOfDependencies

        # obtain a list of dictionaries that represent a tree structure and dependency paths.
        # ex: [{'G': {'dep__relation': {'purulent': {'acomp__relation': {'drainage': {}}, 'ccomp__relation': ....
        paths = createDependencyPaths(groupOfDependencies)

        #print "path:", paths

        listOfPaths.append(paths)

    return listOfPaths

def getDepenPaths(phrase):
    """
    takes in text and obtains the dependency paths between tokens.

    each new line is processed as a separately.
    """

    # list of list of dictionaries of the form
    # [[{"span":("tok1", "tok2"), "rel":"rel_type__relation"},...]...]
    groupsOfDependencies = getCollapsedDepdencies(phrase)

    listOfPaths = getDepenPathFromGroupOfDependencies(groupsOfDependencies)

    return listOfPaths

if __name__ == "__main__":

     #phrase = ' '.join(['Lungs', ':', 'Clear', 'to', 'A', '+', 'P', 'CV', ':', 'RRR', 'without', 'R /', 'G /', 'M', 'Abd :', '+', 'BS', ',', 'soft', ',', 'nontender ,', 'without',
     #'masses', 'or', 'hepatosplenomegaly', 'Chest', ':', 'wound', 'w', '/', 'purulent drainage ,', 'sternum', 'stable', '.'])

#    phrase = 'On [ * * 01 - 14 * * ] she was readmitted to [ * * Hospital 1872 * * ] with fever , WBC , and purulent drainage from her sternal wound .\nHowdy, how are you all?\nMy favorite movie is Annie Hall.'

    phrase = "hello, how are 5-- you doing today? I am doing very well. Goodbye"

#    phrase = ['Her', 'wound', 'grew', 'out', 'MRSA', 'and', 'she', 'was', 'continued', 'on', 'Vancomycin', '.']

   # phrase = ['27513', '||||', '8114', '||||', '28155', '||||', 'DISCHARGE_SUMMARY', '||||', '2016', '-', '01', '-', '25', '00', ':', '00', ':', '00', '.', '0', '||||', '||||', '||||', '||||', 'Admission', 'Date', ':', '[', '*', '*', '2016', '-', '01', '-', '15', '*', '*', ']', 'Discharge', 'Date', ':', '[', '*', '*', '2016', '-', '01', '-', '25', '*', '*', ']', 'Date', 'of', 'Birth', ':', '[', '*', '*', '1955', '-', '07', '-', '30', '*', '*', ']', 'Sex', ':', 'F', 'Service', ':', 'CARDIOTHORACIC', 'Allergies', ':', 'Patient', 'recorded', 'as', 'having', 'No', 'Known', 'Allergies', 'to', 'Drugs', 'Attending', ':', '[', '*', '*', 'Attending', 'Info', '565', '*', '*', ']', 'Chief', 'Complaint', ':', '60', 'year', 'old', 'white', 'female', 's', '/', 'p', 'CABG', '[', '*', '*', '2016', '-', '01', '-', '05', '*', '*', ']', 'with', 'fever', 'and', 'sternal', 'wound drainage .'] 

    #phrase = ['cigs', ':', 'none', 'ETOH', ':', 'none', 'Family', 'History', ':', 'unremarkable', 'Physical', 'Exam', ':', 'Elderly', 'white', 'female', 'in', 'NAD', 'Temp', ':', '100', 'VSS', 'HEENT', ':', 'NC', '/', 'AT', ',', 'PERLA', ',', 'EOMI', ',', 'oropharynx', 'benign', 'Neck', ':', 'supple', ',', 'FROM', ',', 'no', 'lymphadenopathy', 'or', 'thyromegaly ,', 'carotids', '2', '+', '=bilat', '.']
 
    #phrase = ['Past', 'Medical', 'History', ':', 's', '/', 'p', 'CABG', '[', '*', '*', '2016', '-', '01', '-', '05', '*', '*', ']', 'NIDDM', 'Arthritis', 'Anxiety', 'HTN', 'Depression', 's', '/', 'p', 'CCY', 's', '/', 'p', 'TAH', 's', '/', 'p', 'tubal', 'ligation', 'Social', 'History', ':', 'Lives', 'with', 'husband', '.']


#    phrase = " ".join(phrase)

    print phrase.split(' ')

    depenPaths = getDepenPaths(phrase)

#    print depenPaths
#    print len(depenPaths)

#    print followDependencyPath("wound", "MRSA", depenPaths)
