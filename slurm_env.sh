#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem-per-cpu=4G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=48
#SBATCH --time=03:00:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

module load python/3.11 scipy-stack
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt
# python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/sensedoc/ETL/utilities.py
python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/sensedoc/ETL/load.py /home/btcrchum/projects/def-dfuller/interact/data_archive
