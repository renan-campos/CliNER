######################################################################
#  CliNER - cli.py                                                   #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Command Line Interface for working with CliNER.          #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Oct. 5, 2014'



import click
import os
import sys
import subprocess
import glob

from note import Note


@click.group()
def clicon():
    pass


supported_formats_help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )"


# Train
@clicon.command()
@click.option('--annotations'     , help='Concept files for training.'  )
@click.option('--model'           , help='Model output by train.'       )
@click.option('--format'          , help=supported_formats_help         )
@click.option('--grid/--no-grid'  , help='Flag that enables grid search', 
              default=False)
@click.option('--crf/--no-crf'    , help='Flag that enables crfsuite'   ,
              default=True)
@click.option('--third/--no-third', help='Flag that enables third pass' ,
              default=False)
@click.argument('input')
def train(annotations, model, format, grid, crf, third, input):

    # training data needs concept file annotations
    if not annotations:
        print >>sys.stderr, '\n\tError: Must provide annotations for text files'
        print >>sys.stderr,  ''
        exit(1)

    # Base directory
    BASE_DIR = os.environ.get('CLICON_DIR')
    if not BASE_DIR:
        raise Exception('Environment variable CLICON_DIR must be defined')

    # Executable
    runable = os.path.join(BASE_DIR, 'clicon/train.py')

    # Build command
    cmd = ['python', runable, '-t', input]

    # Arguments
    if annotations:
        cmd += ['-c', annotations]
    if model:
        cmd += ['-m',       model]
    if format:
        cmd += ['-f',      format]
    if grid:
        cmd += ['-g']
    if not crf:
        cmd += ['-no-crf']
    if third:
        cmd += ['-third']

    # Execute train.py
    subprocess.call(cmd)




# Predict
@clicon.command()
@click.option('--out'   , help='The directory to write the output')
@click.option('--model' , help='Model used to predict on files'   )
@click.option('--format', help=supported_formats_help             )
@click.option('--third/--no-third', help='Flag that enables third pass' ,
              default=False)
@click.argument('input')
def predict(model, out, format, third, input):

    # Base directory
    BASE_DIR = os.environ.get('CLICON_DIR')
    if not BASE_DIR:
        raise Exception('Environment variable CLICON_DIR must be defined')

    # Executable
    runable = os.path.join(BASE_DIR,'clicon/predict.py')

    # Build command
    cmd = ['python', runable, '-i', input]

    # Optional arguments
    if out:
        cmd += ['-o',    out]
    if model:
        cmd += ['-m',  model]
    if format:
        cmd += ['-f', format]
    if third:
        cmd += ['-third']

    # Execute train.py
    subprocess.call(cmd)





# Evaluate
@clicon.command()
@click.option('--predictions', help='Directory where predictions  are stored.')
@click.option('--gold'       , help='Directory where gold standard is stored.')
@click.option('--out'        , help='Output file'                             )
@click.option('--format'     , help=supported_formats_help                    )
@click.argument('input')
def evaluate(predictions, gold, out, format, input):

    # Base directory
    BASE_DIR = os.environ.get('CLICON_DIR')
    if not BASE_DIR:
        raise Exception('Environment variable CLICON_DIR must be defined')

    # Executable
    runable = os.path.join(BASE_DIR,'clicon/evaluate.py')

    # Build command
    cmd = ['python', runable, '-t', input]

    # Optional arguments
    if predictions:
        cmd += ['-c', predictions]
    if gold:
        cmd += ['-r',        gold]
    if out:
        cmd += ['-o',         out]
    if format:
        cmd += ['-f',      format]

    # Execute train.py
    subprocess.call(cmd)





# Format
@clicon.command()
@click.option('--annotations', help='Concept files for training.')
@click.option('--format'     , help=supported_formats_help       )
@click.option('--out'        , help='File to write the output.'  )
@click.argument('input')
def format(annotations, format, out, input):

    # Base directory
    BASE_DIR = os.environ.get('CLICON_DIR')
    if not BASE_DIR:
        raise Exception('Environment variable CLICON_DIR must be defined')

    # Executable
    runable = os.path.join(BASE_DIR,'clicon/format.py')

    # Build command
    cmd = ['python', runable, flag, input]

    # Optional arguments
    if annotations:
        cmd += ['-a', annotations]
    if out:
        cmd += ['-o',         out]
    if format:
        cmd += ['-f',      format]

    # Execute train.py
    subprocess.call(cmd)




if __name__ == '__main__':
    clicon()


