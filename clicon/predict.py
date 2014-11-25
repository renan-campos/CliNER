######################################################################
#  CliNER - predict.py                                               #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Use trained model to predict concept labels for data.    #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Oct. 5, 2014'


import os
import sys
import glob
import argparse
import helper
import re
import string

from model import Model
from notes.note import Note

from features_dir.umls_dir.interpret_umls import obtain_concept_id

sys.path.append((os.environ["CLICON_DIR"] + "/clicon/features_dir/umls_dir"))

from umls_cache import UmlsCache

import itertools
import cPickle as pickle

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", 
        dest = "input", 
        help = "The input files to predict", 
        default = os.path.join(os.getenv('CLICON_DIR'), 'data/test_data/*')
    )

    parser.add_argument("-o", 
        dest = "output", 
        help = "The directory to write the output", 
        default = os.path.join(os.getenv('CLICON_DIR'), 'data/test_predictions')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The model to use for prediction",
        default = os.path.join(os.getenv('CLICON_DIR'), 'models/run.model')
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )", 
        default = 'i2b2'
    )

    parser.add_argument("-crf",
        dest = "with_crf",
        help = "Specify where to find crfsuite",
 
      default = None
    )

    #print "testing concept id lookup"

    #testConceptLookup()

    #return

    args = parser.parse_args()


    # Parse arguments
    files = glob.glob(args.input + "/*")

    #print files

    helper.mkpath(args.output)
    format = args.format


    # Predict
    predict(files, args.model, args.output, format=format)



def predict(files, model_path, output_dir, format):

    # Must specify output format
    if format not in Note.supportedFormats():
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: ', ' | '.join(Note.supportedFormats())
        print >>sys.stderr, ''
        exit(1)



    # Load model
    model = Model.load(model_path)


    # Tell user if not predicting
    if not files:
        print >>sys.stderr, "\n\tNote: You did not supply any input files\n"
        exit()


    # For each file, predict concept labels
    n = len(files)
    for i,txt in enumerate(sorted(files)):

        # Read the data into a Note object
        note = Note(format)
        note.read(txt)


        print '-' * 30
        print '\n\t%d of %d' % (i+1,n)
        print '\t', txt, '\n'


        # Predict concept labels
        labels = model.predict(note)

        # Output file
        extension = note.getExtension()
        fname = os.path.splitext(os.path.basename(txt))[0] + '.' + extension
        out_path = os.path.join(output_dir, fname)

        # Get predictions in proper format
        note.setFileName(os.path.split(txt)[-1])
        output = note.write(labels)

        # task B
        if format == "semeval":
            # for the spans generated obtain concept ids of phrase
            output = taskB(output, txt)

        # Output the concept predictions
        print '\n\nwriting to: ', out_path
        with open(out_path, 'w') as f:
            print >>f, output
        print

def testConceptLookup():
    """
    test how well concept id lookup performs

    NOTE: can be deleted.
    """

    cache = UmlsCache()    

    filter = ["T020", # acquired abnormality
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
                                         "T184"]

    pipeFilePaths = glob.glob("../../clicon_home/test/train/pipe/*")

    for fileNum, pipeFilePath in enumerate(pipeFilePaths):

        print fileNum
        print pipeFilePath

        textFilePath = re.sub(r"\.pipe", ".text", pipeFilePath)
        textFilePath = re.sub(r"(?<=/)pipe", "text", textFilePath)

        textFile = open(textFilePath, "r")
        textFileTxt = textFile.read()
        textFile.close()

        pipeFile = open(pipeFilePath, "r")
        pipeFileTxt = pipeFile.read()
        pipeFile.close()

        linesInPipeFileTxt = pipeFileTxt[:-1].split('\n')
        
        cuis = []

        newPipeText = []

        for line in linesInPipeFileTxt:
            line = line.split('||')

            phrase = ""

            # get the phrase  for each span
            for span in pairwise(line[3:]):

                string = textFileTxt[int(span[0]):int(span[1])+1]

                phrase += string

            cui = obtain_concept_id(cache, phrase, filter)

            if cui != line[2]:
                print "\n"
                print "gold standard cui: "
                print line[2]

                print "cui found: "
                print cui

                print "phrase: "
                print phrase
                print "\n"

            line[2] = cui

            newPipeText.append("||".join(line))

        newPipeText += [""]

        newPipeText = "\n".join(newPipeText)
            
        pipeFile = open(pipeFilePath, "wb")
        pipeFile.write(newPipeText)
        pipeFile.close()
    
def taskB(outputArg, txtFile):
    """
    obtains concept ids for each phrase indicated by the span generated from prediction
    """

    cache = UmlsCache()

    filter = ["T020", # acquired abnormality
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
              "T184"]

    txtFile = open(txtFile, "r")

    txtFile = txtFile.read()

    # remove end new line since it is junk.
    output = outputArg[:-1]

    # turn output into a list of strings.
    output = output.split('\n')

    cuisToInsert = []

    for index, line in enumerate(output):

        line = line.split("||")

        phrase = ""

        # get the phrase  for each span
        for span in pairwise(line[3:]):

            string = txtFile[int(span[0]):int(span[1])+1]

            phrase += string

        # concept Id of phrase
        conceptId = obtain_concept_id(cache, phrase, filter)

        cuiToInsert = {}

        cuiToInsert["index"] = index
        cuiToInsert["cui"] = conceptId
 
        cuisToInsert.append(cuiToInsert)

    for cuiToInsert in cuisToInsert:
        # replace CUI-less with concept id obtained
        string = output[cuiToInsert["index"]]

        string = re.sub("CUI-less", cuiToInsert["cui"], string)

        output[cuiToInsert["index"]] = string

    # gets end new line back when hoining
    output += [""]

    resultingOutput = "\n".join(output)

    return resultingOutput

if __name__ == '__main__':
    main()
