#!/bin/bash
#SBATCH --account=def-dfuller
#SBATCH --mem=4G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=3:00:00
#SBATCH --mail-user=benoit.thierry@umontreal.ca
#SBATCH --mail-type=ALL

#tar -cvzf  $SCRATCH/data_archive.tar.gz data_archive
tar -cvzf  $SCRATCH/data_archive_w4.tar.gz data_archive/montreal/wave_04/sensedoc data_archive/victoria/wave_04/sensedoc 