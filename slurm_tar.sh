#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem-per-cpu=4G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=48
#SBATCH --time=03:00:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

tar -cv --use-compress-program=zstd -f  $SCRATCH/data_archive.tar.zst /home/btcrchum/projects/def-dfuller/interact/data_archive