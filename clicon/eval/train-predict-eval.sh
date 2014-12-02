#!/bin/sh

# Run this for end-to-end analysis of system

TRAIN_FILES="00098-016139"
#TRAIN_FILES="*"
#TRAIN_FILES="02115-010823"

TEST_FILES="10101-012638"
#TEST_FILES="*"

# Train model
clicon train "$CLICON_DIR/data/semeval/train/txt/$TRAIN_FILES.text" --annotations "$CLICON_DIR/data/semeval/train/con/$TRAIN_FILES.pipe" --format semeval --third
#clicon train "$CLICON_DIR/data/semeval/train/txt/$TRAIN_FILES.text" --annotations "$CLICON_DIR/data/semeval/train/con/$TRAIN_FILES.pipe" --format semeval

# Gather evaluation data
rm -f $CLICON_DIR/clicon/eval/run-data/gold/*
#cp $CLICON_DIR/data/semeval/train/con/$TRAIN_FILES.pipe $CLICON_DIR/clicon/eval/run-data/gold
cp $CLICON_DIR/data/semeval/test/con/$TEST_FILES.pipe $CLICON_DIR/clicon/eval/run-data/gold

# Predict
rm -f $CLICON_DIR/clicon/eval/run-data/predict/*
#clicon predict "$CLICON_DIR/data/semeval/train/txt/$TRAIN_FILES.text" --format semeval --out $CLICON_DIR/clicon/eval/run-data/predict --third
clicon predict "$CLICON_DIR/data/semeval/test/txt/$TEST_FILES.text" --format semeval --out $CLICON_DIR/clicon/eval/run-data/predict


# Run eval script
perl $CLICON_DIR/clicon/eval/semevaluate.pl -input $CLICON_DIR/clicon/eval/run-data/predict/ -gold $CLICON_DIR/clicon/eval/run-data/gold -n train-and-test-output -r 1 -t A
cat train-and-test-output.1.A.noadd


# Clean up
#rm $CLICON_DIR/clicon/eval/run-data/predict/*
rm  train-and-test-output.1.A.noadd
