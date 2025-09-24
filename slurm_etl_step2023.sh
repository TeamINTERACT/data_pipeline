#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem-per-cpu=4G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --time=0:15:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

module load StdEnv/2023 postgresql/16.0 python/3.10 scipy-stack
source venv_stepcount2023/bin/activate
python /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/sensedoc/ETL/top_step.py /home/btcrchum/projects/def-dfuller/interact/data_archive
