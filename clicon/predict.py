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
import time

from model import Model
from notes.note import Note

from features_dir.umls_dir.interpret_umls import obtain_concept_id

sys.path.append((os.environ["CLICON_DIR"] + "/clicon/features_dir/umls_dir"))
sys.path.append((os.environ["CLICON_DIR"] + "/clicon/normalization/spellCheck"))

from spellChecker import getPWL
from umls_cache import UmlsCache

import itertools
import cPickle as pickle

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

    parser.add_argument("-third",
        dest = "third",
        help = "A flag indicating whether to have third/clustering pass",
        action = "store_true"
    )

    args = parser.parse_args()

    files = glob.glob(args.input)

    helper.mkpath(args.output)
    format = args.format
    third = args.third


    # Tell user if not predicting
    if not files:
        print >>sys.stderr, "\n\tNote: You did not supply any input files\n"
        exit()


    # Load model
    model = Model.load(args.model)


    # Predict
    predict(files, model, args.output, format=format, third=third)



def predict(files, model, output_dir, format, third=False):

    # Must specify output format
    if format not in Note.supportedFormats():
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: ', ' | '.join(Note.supportedFormats())
        print >>sys.stderr, ''
        exit(1)
   
    # For each file, predict concept labels
    n = len(files)
    for i,txt in enumerate(sorted(files)):

        # Read the data into a Note object
        note = Note(format)
        note.read(txt)
       
        # Predict concept labels
        print "predicting"
        labels = model.predict(note, third)
        print "FINISHED PREDICTING"
        
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

def taskB(outputArg, txtFile):
    """
    obtains concept ids for each phrase indicated by the span generated from prediction
    """

    pwl = getPWL()
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

    # turn output into a list of strings.
    output = outputArg.split('\n')

    cuisToInsert = []

    for index, line in enumerate(output):

        phrase = ""

        spans = line.split("|")[1]
        spans = spans.split(',')
        spans = [s.split('-') for s in spans]
        
        # get the phrase  for each span
        for span in spans:

            string = txtFile[int(span[0]):int(span[1])+1]

            phrase += string

        conceptId = obtain_concept_id(cache, phrase, filter, PyPwl=pwl)

        cuiToInsert = {}

        cuiToInsert["index"] = index
        cuiToInsert["cui"] = conceptId
 
        cuisToInsert.append(cuiToInsert)

    for cuiToInsert in cuisToInsert:
        # replace CUI-less with concept id obtained
        string = output[cuiToInsert["index"]]

        string = re.sub("CUI-less", cuiToInsert["cui"], string)

        output[cuiToInsert["index"]] = string

    resultingOutput = "\n".join(output)

    return resultingOutput

if __name__ == '__main__':
    main()
