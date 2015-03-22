#
#  Willie Boag                 wboag@cs.uml.edu
#
#  CliNER - install_genia.sh
#


# Installation log
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
log="$GENIA_DIR/log_installation.txt"
echo "" > $log

echo -e "\nSee genia installation details at: \n\t$GENIA_DIR/log_installation.txt\n"



# Get sources
cd $CLINER_DIR/cliner/features_dir/genia_dir
wget http://www.nactem.ac.uk/tsujii/GENIA/tagger/geniatagger-3.0.1.tar.gz &>> $log
tar xzvf geniatagger-3.0.1.tar.gz &>> $log
rm geniatagger-3.0.1.tar.gz

# Build GENIA tagger
cd geniatagger-3.0.1/
echo "$(sed '1i#include <cstdlib>' morph.cpp)" > morph.cpp # fix build error
echo "building GENIA tagger"
make &>> $log
echo -e "GENIA tagger built\n"

# Successful build ?
if ! [[ $? -eq 0 ]] ; then
    echo "there was a build error in GENIA"
    return
fi

# Set config file location of tagger
if [[ ! -f "$CLINER_DIR/config.txt" ]] ; then
    echo -e "\tWarning: Could not update config.txt because CLINER_DIR must be an absolute path\n"
    cd $old_path
    return
fi
config_file="$CLINER_DIR/config.txt"
out_tmp="out.tmp.txt"
echo "GENIA $(pwd)/geniatagger" > $out_tmp
while read line ; do
    if ! [[ $line = GENIA* ]] ; then
        echo $line >> $out_tmp
    fi
done < "$config_file"
mv $out_tmp $config_file

