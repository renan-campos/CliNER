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

sys.path.append( os.path.join( os.path.dirname(__file__), "notes" ) )
print sys.path

from note import Note

@click.group()
def cliner():
    pass


supported_formats_help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )"


# Train
@cliner.command()
@click.option('--annotations'   , help='Concept files for training.'  )
@click.option('--model'         , help='Model output by train.'       )
@click.option('--format'        , help=supported_formats_help         )
@click.option('--grid/--no-grid', help='Flag that enables grid search',
              default=False)
@click.option('--crf/--no-crf'  , help='Flag that enables crfsuite'   ,
              default=True)
@click.argument('input')
def train(annotations, model, format, grid, crf, input):

    # training data needs concept file annotations
    if not annotations:
        print >>sys.stderr, '\n\tError: Must provide annotations for text files'
        print >>sys.stderr,  ''
        exit(1)

    # Base directory
    BASE_DIR = os.path.dirname(__file__)

    # Executable
    runable = os.path.join(BASE_DIR, 'train.py')

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

    # Execute train.py
    subprocess.call(cmd)




# Predict
@cliner.command()
@click.option('--out'   , help='The directory to write the output')
@click.option('--model' , help='Model used to predict on files'   )
@click.option('--format', help=supported_formats_help             )
@click.argument('input')
def predict(model, out, format, input):

    # Base directory
    BASE_DIR = os.path.dirname(__file__)

    # Executable
    runable = os.path.join(BASE_DIR, 'predict.py')

    # Build command
    cmd = ['python', runable, '-i', input]

    # Optional arguments
    if out:
        cmd += ['-o',    out]
    if model:
        cmd += ['-m',  model]
    if format:
        cmd += ['-f', format]

    # Execute train.py
    subprocess.call(cmd)





# Evaluate
@cliner.command()
@click.option('--predictions', help='Directory where predictions  are stored.')
@click.option('--gold'       , help='Directory where gold standard is stored.')
@click.option('--out'        , help='Output file'                             )
@click.option('--format'     , help=supported_formats_help                    )
@click.argument('input')
def evaluate(predictions, gold, out, format, input):

    # Base directory
    BASE_DIR = os.path.dirname(__file__)

    # Executable
    runable = os.path.join(BASE_DIR,'evaluate.py')

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
@cliner.command()
@click.option('--annotations', help='Concept files for training.')
@click.option('--format'     , help=supported_formats_help       )
@click.option('--out'        , help='File to write the output.'  )
@click.argument('input')
def format(annotations, format, out, input):

    # Base directory
    BASE_DIR = os.path.dirname(__file__)

    # Executable
    runable = os.path.join(BASE_DIR, 'format.py')

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
    cliner()


