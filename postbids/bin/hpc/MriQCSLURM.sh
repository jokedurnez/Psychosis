#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --mem=16GB
#SBATCH -p hns,normal,russpold
#SBATCH --output=logs/QC.%a.txt
#SBATCH --error=logs/QC.%a.txt
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=2
#SBATCH --ntasks=1

source $HOME/Psychosis/config_sherlock.sh

#select subject
if [ -z "$SUBJECT" ]; then
    SUBJECT=$(singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $CLEANSINGULARITY python $CODEDIR/postbids/bin/scripts/grab_subject_id.py 2>&1)
fi

# exit when the pipeline does not execute
set PYTHONPATH=""
set -e

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Started MRIQC for subject $SUBJECT"
echo "============================================================================================"

# run MRIQC
set -o xtrace
singularity run -B $OAK:$OAK -B $SCRATCH:$SCRATCH $MRIQCSINGULARITY -v --participant_label=$SUBJECT -w $LOCAL_SCRATCH --mem_gb=32 $BIDSDIR $MRIQCDIR participant
set +o xtrace

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Finished MRIQC for subject $SUBJECT"
echo "============================================================================================"
