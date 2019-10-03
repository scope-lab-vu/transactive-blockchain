#!/bin/bash

#FNCS env vars - FNCS_INSTALL needs to be updated with FNCS install location
export FNCS_INSTALL="$HOME/FNCS_install"

# update LD_LIBRARY_PATH
if test "x$LD_LIBRARY_PATH" = x
then
    export LD_LIBRARY_PATH="$FNCS_INSTALL/lib"
else
    export LD_LIBRARY_PATH="$FNCS_INSTALL/lib:$LD_LIBRARY_PATH"
fi

# update PATH
if test "x$PATH" = x
then
    export PATH="$FNCS_INSTALL/bin"
else
    export PATH="$FNCS_INSTALL/bin:$PATH"
fi

#GridLAB-D env vars
export GLPATH=$FNCS_INSTALL/bin:$FNCS_INSTALL/lib/gridlabd:$FNCS_INSTALL/share/gridlabd/ 
export GRIDLABD=$FNCS_INSTALL/lib/gridlabd/

export hours=12
#export startTime='2013-07-01 10:00:00'
#export stopTime='2013-07-01 11:00:00'
export RIAPS=True