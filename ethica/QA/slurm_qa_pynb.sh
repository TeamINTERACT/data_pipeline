#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem-per-cpu=8G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --time=3:00:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

module load StdEnv/2023 python/3.11 scipy-stack/2026a arrow/25.0.0
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index polars tqdm
pip install --no-index ipykernel jupyterlab
jupyter nbconvert --to notebook --execute --inplace elite_file_QA.ipynb
