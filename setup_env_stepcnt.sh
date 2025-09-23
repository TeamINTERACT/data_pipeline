#!/bin/bash
# Stepcount is not compatible with latest StdEnv
module load StdEnv/2020
# Stepcount need Python<3.11
module load python/3.10 scipy-stack 
module list
# Python Env
virtualenv --no-download venv_stepcount 
source venv_stepcount/bin/activate
pip install --no-index --upgrade pip
pip install stepcount