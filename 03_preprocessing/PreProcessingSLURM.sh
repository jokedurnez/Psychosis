#!/bin/bash
#SBATCH --time=30:00:00
#SBATCH --mem=32GB
#SBATCH -p hns,normal
#SBATCH --output=logs/PREP.%a.txt
#SBATCH --error=logs/PREP.%a.txt
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=8
#SBATCH --ntasks=1

source $HOME/Psychosis/config_sherlock.sh

SUBJECT=$(singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $PANDASSINGULARITY python $CODEDIR/misc/grab_subject_id.py 2>&1)

$CODEDIR/03_preprocessing/PreProcessingPipeline.sh $SUBJECT
