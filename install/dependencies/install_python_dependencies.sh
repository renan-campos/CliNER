#
#  Willie Boag      wboag@cs.uml.edu
#
#  CliNER - install_python_dependencies.sh
#


# Installation log
DEPENDENCIES_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
log="$DEPENDENCIES_DIR/log_installation.txt"
echo "" > $log

echo -e "\nSee python dependency details at: \n\t$DEPENDENCIES_DIR/log_installation.txt\n"


#modules=(nltk python-crfsuite nose numpy scipy scikit-learn marisa-trie)
modules=(nltk python-crfsuite numpy scipy scikit-learn marisa-trie)
for m in ${modules[@]} ; do

    echo -e "\nmodule: $m"

    # Install module if necessary
    python $DEPENDENCIES_DIR/is_installed.py $m
    if [[ $? != 0 ]] ; then
        echo "installing $m"
        pip install -U $m &>> $log

        if [[ $? != 0 ]] ; then
            echo -e "\tERROR installing $m (see log)"
        else
            echo -e "\t$m installed successfully\n"
        fi
    else
        echo -e "\t$m already installed\n"
    fi

done


# Install nltk data
echo "downloading nltk data"
python -m nltk.downloader maxent_treebank_pos_tagger wordnet punkt &>> $log
echo -e "nltk download complete\n"

