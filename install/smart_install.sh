#
# Willie Boag            wboag@cs.uml.edu
#
# CliNER - smart_install.sh
#
# NOTE: Must be run with 'source'
#

# 'install' directory
INSTALL_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# set CLINER_INSTALL_DIR variable
source $INSTALL_DIR/cliner_dir/set_cliner_dir.sh

# python dependencies (use source because of virtualenv)
source $INSTALL_DIR/dependencies/install_python_dependencies.sh

# install 'cliner' command
bash $INSTALL_DIR/build/build_cliner.sh
