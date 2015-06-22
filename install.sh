#
# Willie Boag            wboag@cs.uml.edu
#
# CliNER - smart_install.sh
#
# NOTE: Must be run with 'source'
#

# 'install' directory
BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# set CLINER_INSTALL_DIR variable
source $BASE_DIR/install/cliner_dir/set_cliner_dir.sh

# python dependencies (use source because of virtualenv)
source $BASE_DIR/install/dependencies/install_python_dependencies.sh

# install 'cliner' command
bash $BASE_DIR/install/build_cliner/build_cliner.sh
