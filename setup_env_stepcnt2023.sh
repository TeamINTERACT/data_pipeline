#!/bin/bash
# Stepcount is not compatible with latest StdEnv2023 out of the box
# Biggest problem is the required torch version (1.13) which is not 
# available in StdEnv2023. Yet stepcount works well with more recent
# versions, as long as we control the modules taht are installed
module load StdEnv/2023
# Stepcount need Python<3.11
module load python/3.10 scipy-stack 
module list

# Python Env
virtualenv --no-download venv_stepcount 
source venv_stepcount/bin/activate
pip install --no-index --upgrade pip
pip install --no-deps stepcount
pip install "numpy < 2"
pip install "pandas < 2.1.0"
pip install actipy hmmlearn imbalanced-learn joblib numba scikit-learn torchvision tqdm transforms3d
