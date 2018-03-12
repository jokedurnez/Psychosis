#!/bin/bash
#SBATCH --time=03:00:00
#SBATCH --mem=32GB
#SBATCH -p russpold,normal,hns
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=4

source $HOME/Psychosis/config_sherlock.sh

export PYTHONPATH=""

#select subject
if [ -z "$SUBJECT" ]; then
    SUBJECT=$(singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $CLEANSINGULARITY python $CODEDIR/prebids/bin/scripts/grab_subject_id.py 2>&1)
fi

set -e

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Started bidsifying $SUBJECT"
echo "============================================================================================"

$CODEDIR/prebids/bin/02_bids.sh $SUBJECT

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Finished bidsifying $SUBJECT"
echo "============================================================================================"
