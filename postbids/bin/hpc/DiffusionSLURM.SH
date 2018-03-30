#!/bin/bash
#SBATCH --time=30:00:00
#SBATCH --mem=32GB
#SBATCH -p hns,normal,russpold
#SBATCH --output=logs/DWI.%a.txt
#SBATCH --error=logs/DWI.%a.txt
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=8
#SBATCH --ntasks=1

source $HOME/Psychosis/config_sherlock.sh

SUBJECT=$(singularity exec -B $OAK:$OAK $CLEANSINGULARITY python $CODEDIR/postbids/bin/scripts/grab_subject_id.py 2>&1)

unset PYTHONPATH

singularity run \
    -B $OAK:$OAK \
    -B $MISCDIR/license.txt:/opt/freesurfer/license.txt \
    -B /home/users/jdurnez/Psychosis/postbids/bin/hpc/test/DiffPreprocPipeline_Eddy.sh:/opt/HCP-Pipelines/DiffusionPreprocessing/DiffPreprocPipeline_Eddy.sh \
    -c \
    $HCPPIPELINESSINGULARITY \
    $BIDSDIR $PREPDIR \
    participant \
    --participant_label $SUBJECT \
    --n_cpus 8 \
    --stages 'DiffusionPreprocessing'
