#!/bin/bash
#SBATCH --time=02:00:00
#SBATCH --mem=32GB
#SBATCH -p normal,hns
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=4

source $HOME/Psychosis/config_sherlock.sh

set -e

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Started initiation of psychosisproject"
echo "============================================================================================"

singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $CLEANSINGULARITY python $CODEDIR/prebids/bin/00_generate_bids_folder.py
singularity exec -B $OAK:$OAK -B $SCRATCH:$SCRATCH $CLEANSINGULARITY python $CODEDIR/prebids/bin/01_generate_database.py

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Finished initiation of psychosisproject"
echo "============================================================================================"
