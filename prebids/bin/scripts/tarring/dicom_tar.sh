#!/bin/bash

#SBATCH --job-name=tar
#SBATCH --output=tar.out
#SBATCH --error=tar.err
#SBATCH --time=23:00:00
#SBATCH --mem=64GB
#SBATCH -p russpold,hns,normal
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --mail-type=ALL   # email me when the job starts

source $HOME/Psychosis/config_sherlock.sh

python $PSYDIR/misc/dicom_tar.py
