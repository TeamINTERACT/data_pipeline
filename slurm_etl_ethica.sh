#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem-per-cpu=32G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --time=2:00:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

module load StdEnv/2023 python/3.11 scipy-stack/2023b arrow/25.0.0
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
module load proj # Need to be loaded once venv is activated
pip install --no-index --upgrade pip
# pip install -r requirements.txt
pip install --no-index tabulate SQLAlchemy resampy psycopg2 polars
 python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/ethica/ETL/validate.py /home/btcrchum/projects/def-dfuller/interact/data_archive
# python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/ethica/ETL/load.py /home/btcrchum/projects/def-dfuller/interact/data_archive 4
# python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/ethica/ETL/top.py /home/btcrchum/projects/def-dfuller/interact/data_archive 4
