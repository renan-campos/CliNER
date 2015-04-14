===============================
CliNER
===============================

Clinical Named Entity Recognition system (CliNER) is an open-source natural language processing system for named entity recognition in clinical text of electronic health records.  CliNER system is designed to follow best practices in clinical concept extraction, as established in i2b2 2010 shared task.

CliNER is implemented as a two-pass machine learning system for named entity recognition, currently using a Conditional Random Fields (CRF) classifier to establish concept boundaries and a Support Vector Machine (SVM) classifier to establish the type of concept.

Please note that for optimal performance, CliNER requires the users to obtain a Unified Medical Language System (UMLS) license, since UMLS Metathesaurus is used as one of the knowledge sources for the above classifiers.


* Free software: Apache v2.0 license
* Documentation: http://cliner.readthedocs.org.


Quick Installation
--------

    You will need the following python modules (which can be installed with pip):

        - nose
        - numpy
        - scikit-learn
        - scipy
        - nltk
        - python-crfsuite

    You will also need to run nltk's downloader to get some additional tools:

        - maxent_treebank_pos_tagger
        - wordnet

    Unfortuantely, we cannot provide you with the licensed training data (from i2b2), so for a fully functioning model, you will need to train on your own annotated data.

    Optional: for additional performance, download some tables from the UMLS Metathesaurus. See the detailed installation section for more info on that.


**Test Successful Installation**


Detailed Installation
--------

**Cloning the CliNER git repository:**

::

    user@your-machine:~$ git clone https://github.com/text-machine-lab/CliNER.git
        Cloning into 'CliNER'...
        remote: Counting objects: 1296, done.
        remote: Compressing objects: 100% (503/503), done.
        remote: Total 1296 (delta 812), reused 1253 (delta 781)
        Receiving objects: 100% (1296/1296), 1001.14 KiB | 759 KiB/s, done.
        Resolving deltas: 100% (812/812), done.


**CliNER Dependencies Diagnosis**

We know that software installation can be a major hassle. We hate it too. That's why why made the 'install' directory. This directory contains diagnostic tools to determine what is causing the system installation to fail. We hope you'll never have to use it. To run the full suite of checks, do:

    ::

        user@your-machine:~$ python install/diagnose.py

Good luck!



**Using an installation script**

Linux users can use an installation script to install this project. Note that it cannot get tools and data that require special use agreements (namely, i2b2 data and the UMLS tables), which have to be obtained separately.

To invoke the script, ensure you are in a bash terminal (zsh will not work). Next, ``cd`` into the ``CliNER`` directory:

::

    user@your-machine:~$ cd CliNER
    user@your-machine:~/CliNER$ source install.sh


The script begins with a diagnostic to see what needs to be installed. If the script fails, you should ensure the following systems are installed on your system:

::

    python-pip
    python-dev
    g++
    gfortran
    libopenblas-dev
    liblapack-dev

For Ubuntu users, the above are the names of the packages that need to be installed.  A typical command to install a python module on a Debian-flavored Linux is:

::

    apt-get install <package-name>


Although the script is able to build python dependencies via pip, this is a slow process. It would be much faster to obtain binaries of certain python modules and then run the script:

::

    numpy
    scipy
    scikit-learn (version 0.14)


If the installation script encounters issues, please see the README section corresponding to the failure message.

Please email wboag@cs.uml.edu with your installation questions.


**Step-by-step installation instructions:**


(2) Set the CLINER_DIR environment variable

    In order to run CliNER, you must define the CLINER_DIR environment variable.

    **This variable must be the path of the directory created by git.**

    ::

        user@your-machine:~$ export CLINER_DIR=$(pwd)/CliNER



(3) Install dependencies


    Ensure the following packages are installed on the system (they are used for building the required Python dependencies):

        Linux:
            * python-pip
            * python-dev
            * g++
            * gfortran
            * libopenblas-dev
            * liblapack-dev


        Mac OSX (e.g. using [Homebrew](http://brew.sh/)):
            * python
            * gfortran


    Ensure the following python modules are installed:
        * nose
        * numpy
        * scikit-learn (version 0.14)
        * scipy
        * python-crfsuite
        * nltk  (AND run the NLTK downloader)


    ::

        (venv_cliner)user@your-machine:~/CliNER$ sudo apt-get install python-pip python-virtualenv python-dev g++ gfortran libopenblas-dev liblapack-dev -y
        (venv_cliner)user@your-machine:~/CliNER$ pip install nose numpy scikit-learn scipy nltk python-crfsuite
        (venv_cliner)user@your-machine:~/CliNER$ python -m nltk.downloader maxent_treebank_pos_tagger wordnet




(4) Get i2b2 2010 shared task data

    The Data Use and Confidentiality Agreement (DUA) with i2b2 forbids us from redistributing the i2b2 data. In order to gain access to the data, you must go to:

    https://www.i2b2.org/NLP/DataSets/AgreementAR.php

    to register and sign the DUA. Then you will be able to request the data through them.


    Although we cannot provide i2b2 data, there is a sample to demonstrate how the data is formatted (not actual data from i2b2, though). **Here is a very basic description of the data formats.** It is by no means a complete tutorial.

        * $CLINER_DIR/examples/pretend.txt

            This is a text file. Discharge summaries are written out in plaintext, just like this. It is paired with a concept file, which has its annotations.

        * $CLINER_DIR/examples/pretend.con

            This is a concept file. It provides annotations for the concepts (problem, treatment, test) of the text file. The format is as follows - each instance of a concept has one line. The line describes the word span, the line number and token numbers of the span (delimited by white space), and the label of the concept.

        * $CLINER_DIR/examples/pretend.xml

            This is an alternative way to annotate concepts from a discharge summary. Unlike the text/concept files, this format is not in a pair - it provides both the text and annotations for the discharge summary. This format is easier to read.





(5) Install GENIA tagger (optional)

    This is an optional part of installation. Adding the GENIA tagger will improve results of the system's predictions, but it could run without it.

    Steps

        1. First you must download the sources for GENIA. Do that with ``wget http://www.nactem.ac.uk/tsujii/GENIA/tagger/geniatagger-3.0.1.tar.gz``

        2. In order to compile the sources, you may need to edit a C++ so that it has an additional include directive. This should be able to be accomplished by enterring the geniatagger-3.0.1/ directory and running ``echo "$(sed '1i#include <cstdlib>' morph.cpp)" > morph.cpp``

        3. Compile GENIA. Just run ``make``

        4. If you do not have any errors, then the tagger has been built successfully. If there were compile errors, try to resolve them (it'd be one of those "well it works for me" scenarios).

        5. Set the file "$CLINER_DIR/config.txt" so that the line that has "GENIA None" is replaced with "GENIA <path-to-geniatagger-3.0.1/geniatagger>'. This file is how CliNER is able to find and run the tagger.



(6) Get UMLS tables (optional)

    This is an optional part of installation. Adding the UMLS tables will improve results of the system's predictions, but it could run without it.

    In order to use the UMLS tables, you must request a license. See:

    http://www.nlm.nih.gov/databases/umls.html

    You will need to get following tables: **MRREL, MRCON, MRSTY**

    **Put these tables in the $CLINER_DIR/umls_tables directory.**

    In order to tell CliNER that the tables are there, you must edit the file "$CLINER_DIR/config.txt" and change the line saying "UMLS  None" to "UMLS True". This command will do that ``sed -i "s/UMLS  None/UMLS  True/g" $CLINER_DIR/config.txt``

    **The database will be built from the tables when CliNER is run for the first time.**



(7) Create 'cliner' executable script for command-line use

    In order to run CliNER (as done in the usage examples), you must run setup.py.

    As long as the Python dependencies are properly installed, you should be able to run the setup script.

    If it works, you should see a brief help message when invoking cliner with the ``--help`` option:

    ::

            (venv_cliner)user@your-machine:~/CliNER$ python $CLINER_DIR/setup.py install
            (venv_cliner)user@your-machine:~/CliNER$ cliner --help



(8) Run unit tests

    [this section is under construction]



Usage Examples
--------

    Demo Script
    ::
        user@your-machine:~/CliNER$ source install.sh
        (venv_cliner)user@your-machine:~/CliNER$ bash examples/demo.sh


    i2b2 format

        Train model on i2b2-formatted data
        ::
            (venv_cliner)user@your-machine:~/CliNER$ cliner train $CLINER_DIR/examples/pretend.txt --annotations $CLINER_DIR/examples/pretend.con

        Train model on i2b2-formatted data with SVM grid search (NOTE: Currently does not work with sample data because the sample data is too small for cross validation).
        ::
            (venv_cliner)user@your-machine:~/CliNER$ cliner train $CLINER_DIR/examples/pretend.txt --annotations $CLINER_DIR/examples/pretend.con --grid-search

        Predict concepts and output in i2b2 format
        ::
            (venv_cliner)user@your-machine:~/CliNER$ cliner predict $CLINER_DIR/examples/pretend.txt --out $CLINER_DIR/data/test_predictions/

        Evaluation
        ::
            (venv_cliner)user@your-machine:~/CliNER$ cliner evaluate $CLINER_DIR/examples/pretend.txt --gold $CLINER_DIR/examples --predictions $CLINER_DIR/data/test_predictions/ --format i2b2

        Change Format
        ::
            (venv_cliner)user@your-machine:~/CliNER$ cliner format $CLINER_DIR/examples/pretend.txt --annotations $CLINER_DIR/data/test_predictions/pretend.con --format xml


    xml format

        Train model on xml-formatted data
        ::
            (venv_cliner)user@your-machine:~/CliNER$ cliner train $CLINER_DIR/examples/pretend.txt --annotations $CLINER_DIR/examples/pretend.xml --format xml

        Predict concepts and output in xml format
        ::
            (venv_cliner)user@your-machine:~/CliNER$ cliner predict $CLINER_DIR/examples/pretend.txt --out $CLINER_DIR/data/test_predictions/ --format xml

        Evaluation
        ::
            (venv_cliner)user@your-machine:~/CliNER$ cliner evaluate $CLINER_DIR/examples/pretend.txt --gold $CLINER_DIR/examples --predictions $CLINER_DIR/data/test_predictions/ --format xml

        Change Format
        ::
            (venv_cliner)user@your-machine:~/CliNER$ cliner format $CLINER_DIR/data/test_predictions/pretend.xml --format i2b2



Notes

    We recommend using a virtual environment for you python packages.

        Setup a virtual environent. You must re-enable the virtual environment every new session.

        ::

            user@your-machine:~$ virtualenv venv_cliner
            user@your-machine:~$ source venv_cliner/bin/activate


        reference
            https://virtualenv.pypa.io/en/latest/



