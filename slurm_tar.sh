#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem=4G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --time=12:00:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

tar -cvzf  $SCRATCH/data_archive.tar.gz data_archive