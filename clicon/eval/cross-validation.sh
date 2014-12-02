#
# Script for CV of SemEval data
#
# Author: Willie
#


POOL=$CLICON_DIR/clicon/eval/pool
CATEGORY="all"
FILES="*"

# Collect text data into one place
rm -f $CLICON_DIR/clicon/eval/text/*
cp $POOL/$CATEGORY/txt/$FILES $CLICON_DIR/clicon/eval/text

# Collect concept data into one place
rm -f $CLICON_DIR/clicon/eval/gold/*
cp $POOL/$CATEGORY/con/$FILES $CLICON_DIR/clicon/eval/gold

# Run CV on data
rm -f $CLICON_DIR/clicon/eval/predict/*
python cv.py -f 10 #2

# Score predictions
perl $CLICON_DIR/clicon/eval/semevaluate.pl -input $CLICON_DIR/clicon/eval/predict/ -gold $CLICON_DIR/clicon/eval/gold -n output -r 1 -t A
cat output.1.A.noadd

# Clean up
rm $CLICON_DIR/clicon/eval/predict/*
rm output.1.A.noadd

