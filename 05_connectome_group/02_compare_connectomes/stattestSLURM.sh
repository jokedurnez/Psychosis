#!/bin/bash
#SBATCH --time=2:00:00
#SBATCH -p hns,normal
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --mem=8GB
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1

source ~/Psychosis/config_sherlock.sh

singularity exec -B $OAK:$OAK $CLEANSINGULARITY python $CODEDIR/05_connectome_group/02_compare_connectomes/stattest.py
