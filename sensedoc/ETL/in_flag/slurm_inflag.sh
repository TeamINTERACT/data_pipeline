#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --time=1:00:00              # Task max duration
#SBATCH --job-name=in_flag_top1   # Job names
#SBATCH --mem-per-cpu=4096M
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

module load StdEnv/2023 postgresql/16.0
psql -h cedar-pgsql-vm -d interact_db -f in_flag3.sql
