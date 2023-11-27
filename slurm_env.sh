#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem-per-cpu=4G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --time=03:00:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

module load python/3.11 scipy-stack
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
module load proj # Need to be loaded once venv is activated
pip install --no-index --upgrade pip
pip install -r requirements.txt
# python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/sensedoc/ETL/utilities.py
python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/sensedoc/ETL/load.py /home/btcrchum/projects/def-dfuller/interact/data_archive
# python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/sensedoc/ETL/top.py /home/btcrchum/projects/def-dfuller/interact/data_archive
# python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/sensedoc/ETL/top_error.py
