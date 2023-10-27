#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem-per-cpu=1.5G
#SBATCH --time=1:00:00

module load python/3.11 scipy-stack
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt
