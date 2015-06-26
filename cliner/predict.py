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

from model import Model
from notes.note import Note


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",
        dest = "input",
        help = "The input files to predict",
        default = os.path.join(os.getenv('CLINER_DIR'), 'data/test_data/*')
    )

    parser.add_argument("-o",
        dest = "output",
        help = "The directory to write the output",
        default = os.path.join(os.getenv('CLINER_DIR'), 'data/predictions')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The model to use for prediction",
        default = os.path.join(os.getenv('CLINER_DIR'), 'models/run.model')
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

    args = parser.parse_args()


    # Parse arguments
    files = glob.glob(args.input)
    helper.mkpath(args.output)
    format = args.format


    # Predict
    predict(files, args.model, args.output, format=format)



def predict(files, model_path, output_dir, format, out_handle=sys.stdout):

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
        labels = model.predict(note, out_handle)

        # Get predictions in proper format
        extension = note.getExtension()
        output = note.write(labels)

        #print output

        # Output file
        fname = os.path.splitext(os.path.basename(txt))[0] + '.' + extension
        out_path = os.path.join(output_dir, fname)

        # Output the concept predictions
        print '\n\nwriting to: ', out_path
        with open(out_path, 'w') as f:
            print >>f, output
        print




if __name__ == '__main__':
    main()
