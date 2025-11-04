#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem-per-cpu=4G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=3:00:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL
#SBATCH --array=1-4 

echo "Processing wave $SLURM_ARRAY_TASK_ID"
module load StdEnv/2023 postgresql/16.0
psql -h cedar-pgsql-vm -d interact_db -c "\timing" -f met$SLURM_ARRAY_TASK_ID.sql
