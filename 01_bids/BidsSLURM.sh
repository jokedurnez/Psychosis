#!/bin/bash
#SBATCH --time=02:00:00
#SBATCH --mem=32GB
#SBATCH -p normal,hns
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=4

source $HOME/Psychosis/config_sherlock.sh

export PYTHONPATH=""

#select subject
if [ -z "$SUBJECT" ]; then
    SUBJECT=$(singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $PANDASSINGULARITY python $CODEDIR/01_bids/grab_subject.py 2>&1)
fi

set -e

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Started bidsifying $SUBJECT"
echo "============================================================================================"

$CODEDIR/01_bids/BidsPipeline.sh $SUBJECT

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Finished bidsifying $SUBJECT"
echo "============================================================================================"
