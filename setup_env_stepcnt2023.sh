#!/bin/bash
# Stepcount is not compatible with latest StdEnv2023 out of the box
# Biggest problem is the required torch version (1.13) which is not 
# available in StdEnv2023. Yet stepcount works well with more recent
# versions, as long as we control the modules taht are installed
module load StdEnv/2023 postgresql/16.0
# Stepcount need Python<3.11
module load python/3.10 scipy-stack 
module list

# Python Env
virtualenv --no-download --clear venv_stepcount2023 
source venv_stepcount2023/bin/activate
pip install --no-index --upgrade pip
pip install --no-deps stepcount
pip install "numpy < 2"
pip install "pandas < 2.1.0"
pip install actipy hmmlearn imbalanced-learn joblib numba scikit-learn torchvision tqdm transforms3d sqlalchemy psycopg2

## Environment ##
# Package            Version
# ------------------ -------------------------
# actipy             3.8.0
# asttokens          3.0.0+computecanada
# comm               0.2.2+computecanada
# contourpy          1.3.1+computecanada
# cycler             0.12.1+computecanada
# debugpy            1.8.12+computecanada
# decorator          5.1.1+computecanada
# exceptiongroup     1.2.2+computecanada
# executing          2.2.0+computecanada
# filelock           3.19.1+computecanada
# fonttools          4.55.8+computecanada
# fsspec             2025.9.0+computecanada
# greenlet           3.1.1+computecanada
# hmmlearn           0.3.3+computecanada
# imbalanced-learn   0.14.0
# ipykernel          6.29.5+computecanada
# ipython            8.32.0+computecanada
# ipywidgets         8.1.5+computecanada
# jedi               0.19.2+computecanada
# jinja2             3.1.6+computecanada
# joblib             1.5.2+computecanada
# jupyter_client     8.6.3+computecanada
# jupyter_core       5.7.2+computecanada
# jupyterlab_widgets 3.0.13+computecanada
# kiwisolver         1.4.8+computecanada
# llvmlite           0.44.0+computecanada
# MarkupSafe         2.1.5+computecanada
# matplotlib         3.10.0+computecanada
# matplotlib_inline  0.1.7+computecanada
# mpmath             1.3.0+computecanada
# nest_asyncio       1.6.0+computecanada
# networkx           3.4.2+computecanada
# nose               1.3.7+computecanada
# numba              0.61.0+computecanada
# numpy              1.26.4+computecanada
# packaging          24.2+computecanada
# pandas             2.0.2
# parso              0.8.4+computecanada
# patsy              1.0.1+computecanada
# pexpect            4.9.0+computecanada
# pillow             11.1.0+computecanada
# Pillow_SIMD        9.5.0.post2+computecanada
# pip                25.2+computecanada
# platformdirs       3.10.0+computecanada
# prompt_toolkit     3.0.50+computecanada
# psutil             6.1.1+computecanada
# psycopg2           2.9.9
# ptyprocess         0.7.0+computecanada
# pure_eval          0.2.3+computecanada
# pygments           2.19.1+computecanada
# pyparsing          3.2.1+computecanada
# python_dateutil    2.9.0.post0+computecanada
# pytz               2025.1+computecanada
# pyzmq              26.2.1+computecanada
# scikit_learn       1.5.2+computecanada
# scipy              1.15.1+computecanada
# setuptools         80.7.1
# six                1.17.0+computecanada
# SQLAlchemy         2.0.43
# stack_data         0.6.3+computecanada
# statsmodels        0.14.3+computecanada
# stepcount          3.16.2
# sympy              1.13.1+computecanada
# threadpoolctl      3.6.0+computecanada
# torch              2.6.0+computecanada
# torchvision        0.21.0+computecanada
# tornado            6.4.2+computecanada
# tqdm               4.67.1+computecanada
# traitlets          5.14.3+computecanada
# transforms3d       0.4.2
# typing_extensions  4.12.2+computecanada
# tzdata             2025.1+computecanada
# wcwidth            0.2.13+computecanada
# wheel              0.45.1+computecanada
# widgetsnbextension 4.0.13+computecanada