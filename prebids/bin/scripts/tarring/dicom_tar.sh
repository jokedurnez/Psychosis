#!/bin/bash

#SBATCH --job-name=tar
#SBATCH --output=tar.out
#SBATCH --error=tar.err
#SBATCH --time=23:00:00
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=8
#SBATCH --ntasks=1
#SBATCH -p hns,normal
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --mail-type=ALL   # email me when the job starts

source $HOME/Psychosis/config_sherlock.sh

python -i $CODEDIR/prebids/bin/scripts/tarring/dicom_tar.py
