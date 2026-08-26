#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem-per-cpu=8G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=6
#SBATCH --gpus=h100:1
#SBATCH --time=3:00:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

module load StdEnv/2023 cuda/12.6 cudnn/9.10 python/3.11 scipy-stack/2026a arrow/25.0.0
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
module load proj # Need to be loaded once venv is activated
pip install --no-index --upgrade pip
# pip install -r requirements.txt
pip install --no-index tabulate SQLAlchemy resampy psycopg2 polars geopy
# PyPOTS downloaded from login node (see https://docs.alliancecan.ca/wiki/Python#Pre-downloading_packages)
pip install pygrinder-0.7-py3-none-any.whl
pip install pypots-1.5-py3-none-any.whl
pip freeze > requirements_ethica_slurm.txt
# python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/ethica/ETL/validate.py /home/btcrchum/projects/def-dfuller/interact/data_archive
# python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/ethica/ETL/load.py /home/btcrchum/projects/def-dfuller/interact/data_archive
# python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/ethica/QA/elite_file_QA.py
python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/ethica/ETL/top.py $SCRATCH/test_data 0
