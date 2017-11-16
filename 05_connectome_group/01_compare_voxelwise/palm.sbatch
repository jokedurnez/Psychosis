#!/bin/bash
#SBATCH --time=20:00:00
#SBATCH --mem=63GB
#SBATCH -p normal,hns
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=16
#SBATCH --ntasks=1

source $HOME/Psychosis/config_sherlock.sh

CMD=$(singularity exec -B $OAK:$OAK $CLEANSINGULARITY python -i $CODEDIR/05_connectome_group/01_compare_voxelwise/palm.py 2>&1)

$CMD

echo "============================================================================================"
echo "`date`: ༼ つ ◕_◕ ༽つ Finished running palm"
echo "============================================================================================"
