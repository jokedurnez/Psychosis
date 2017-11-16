#!/bin/bash

#SBATCH --job-name=tar
#SBATCH --output=tar.out
#SBATCH --error=tar.err
#SBATCH --time=23:00:00
#SBATCH --mem=64GB
#SBATCH --qos=russpold
#SBATCH -p russpold
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --mail-type=ALL   # email me when the job starts

source /scratch/PI/russpold/data/psychosis/01_code/config_sherlock.sh

python $PSYDIR/01_code/misc/preproc_tar.py
