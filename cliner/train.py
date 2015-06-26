######################################################################
#  CliNER - train.py                                                 #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Build model for given training data.                     #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'June 23, 2015'


import os
import glob
import argparse
import sys
import cPickle as pickle

import helper
from model import Model
from notes.note import Note


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "txt",
        help = "The files that contain the training examples",
        default = os.path.join(os.getenv('CLINER_DIR'), 'data/train/txt/*')
    )

    parser.add_argument("-c",
        dest = "con",
        help = "The files that contain the labels for the training examples",
        default = os.path.join(os.getenv('CLINER_DIR'), 'data/train/con/*')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "Path to the model that should be generated",
        default = os.path.join(os.getenv('CLINER_DIR'), 'models/run.model')
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )",
        default = 'i2b2'
    )

    parser.add_argument("-g",
        dest = "grid",
        help = "A flag indicating whether to perform a grid search",
        action = "store_true"
    )

    parser.add_argument("-no-crf",
        dest = "nocrf",
        help = "A flag indicating whether to use crfsuite for pass one.",
        action = "store_true"
    )

    # Parse the command line arguments
    args = parser.parse_args()
    is_crf = not args.nocrf

    # lists of text & concept file paths
    txt_files = glob.glob(args.txt)
    con_files = glob.glob(args.con)

    # Must specify output format
    if args.format not in Note.supportedFormats():
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: ', ' | '.join(Note.supportedFormats())
        print >>sys.stderr, ''
        exit(1)

    # Collect training data file paths     e.g. {'record-13': 'record-13.con'}
    txt_files_map = helper.map_files(txt_files) 
    con_files_map = helper.map_files(con_files)

    # e.g. training_list =  [ ('record-13.txt', 'record-13.con') ]
    training_list = []
    for k in txt_files_map:
        if k in con_files_map:
            training_list.append((txt_files_map[k], con_files_map[k]))

    # display file names (for user to see data was properly located)
    print '\ntraining on %d files\n' % len(training_list)

    # Train the model
    train(training_list, args.model, args.format, is_crf=is_crf, grid=args.grid)



def train(training_list, model_p, format, is_crf=True, grid=False, out_handle=sys.stdout):

    '''
    train.py :: train()

    Purpose: Build CliNER model from training data

    >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'examples')
    >>> training_list = [ (os.path.join(base_dir,'pretend.txt') ,  \
                           os.path.join(base_dir,'pretend.con') )  ]
    >>> model_path = os.path.join(os.getenv('CLINER_DIR'), 'models', 'testing.model')
    >>> format = 'i2b2'
    >>> is_crf = True
    >>> grid = False

    #>>> out_handle = open('a.txt')

    #>>> train(training_list, model_path, format, is_crf, grid, out_handle)
    
    '''

    # Read the data into a Note object
    notes = []
    for txt, con in training_list:
        note_tmp = Note(format)       # Create Note
        note_tmp.read(txt, con)       # Read data into Note
        notes.append(note_tmp)        # Add the Note to the list

    if not notes:
        print >>sys.stderr, 'Error: Cannot train on 0 files. Terminating train.'
        return 1

    # Create a Machine Learning model
    model = Model(is_crf=is_crf)

    # Train the model using the Note's data
    model.train(notes, grid, out_handle)

    # Pickle dump
    print >>out_handle, 'pickle dump'
    with open(model_p, "wb") as m_file:
        pickle.dump(model, m_file)



if __name__ == '__main__':
    main()
