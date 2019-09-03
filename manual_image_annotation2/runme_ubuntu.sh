#!/usr/bin/env bash

# Functions are not exported by default to be made available in subshells
PROFILE=`which conda`  # get file path to conda
PROFILE=`dirname $PROFILE`  # get directory name condabin
PROFILE=`dirname $PROFILE`  # get Anaconda root dir
source $PROFILE/etc/profile.d/conda.sh

conda info --envs   # list available environments
conda activate DL3  # activate DL3 environment
python runme.py     # start the application
conda deactivate    # deactivate Anaconda
