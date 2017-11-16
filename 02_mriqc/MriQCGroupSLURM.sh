#!/bin/bash
#SBATCH --time=10:00:00
#SBATCH --mem=16GB
#SBATCH -p hns,normal
#SBATCH --output=logs/QC.all.txt
#SBATCH --error=logs/QC.all.txt
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=8
#SBATCH --ntasks=1

source $HOME/Psychosis/config_sherlock.sh

singularity run -B $OAK:$OAK -B $SCRATCH:$SCRATCH $MRIQCSINGULARITY $BIDSDIR $MRIQCDIR/out -w $MRIQCDIR/temp group

singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $MRIQCSINGULARITY mriqc_clf --load-classifier -X $MRIQCDIR/out/T1w.csv #-o $MRIQCDIR/predictions.csv
