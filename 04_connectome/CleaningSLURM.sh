#!/bin/bash
#SBATCH --time=8:00:00
#SBATCH --mem=16GB
#SBATCH -p hns,normal
#SBATCH --output=logs/CLEAN.%a.txt
#SBATCH --error=logs/CLEAN.%a.txt
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=4
#SBATCH --ntasks=1

source $HOME/Psychosis/config_sherlock.sh

#select subject
export SUBJECT=$(singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $PANDASSINGULARITY python $CODEDIR/misc/grab_subject_id.py 2>&1)
unset PYTHONPATH

set -e

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Started cleaning of rest sessions"
echo "============================================================================================"

singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $CLEANSINGULARITY python $CODEDIR/04_connectome/timeseries_clean.py

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Started extracting connectome"
echo "============================================================================================"

singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $CLEANSINGULARITY python $CODEDIR/04_connectome/connectome.py

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Finished analyzing rest sessions"
echo "============================================================================================"
