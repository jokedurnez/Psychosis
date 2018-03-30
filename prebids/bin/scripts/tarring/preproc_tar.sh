#!/bin/bash

#SBATCH --job-name=tar
#SBATCH --output=tar.out
#SBATCH --error=tar.err
#SBATCH --time=23:00:00
#SBATCH --mem=64GB
#SBATCH -p hns,normal
#SBATCH --cpus-per-task=16
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --mail-type=ALL   # email me when the job starts

source /home/jdurnez/Psychosis/config_sherlock.sh
source /share/PI/russpold/software/setup_all.sh

python $CODEDIR/prebids/bin/scripts/tarring/preproc_tar.py
