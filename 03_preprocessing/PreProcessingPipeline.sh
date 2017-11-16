source $HOME/Psychosis/config_sherlock.sh
#module load singularity

# check subjectlabel

export SUBJECTLABEL=$1
#export SUBJECTLABEL=S0492QGT
: "${SUBJECTLABEL?ERROR No subjectlabel passed to script...}"

# remove existing preprocessing directory

rm -rf $PREPDIR/sub-$SUBJECTLABEL

# set LOGDIR

export LOGDIR=$CODEDIR/03_preprocessing/logs/$SUBJECTLABEL
rm -rf $LOGDIR
mkdir $LOGDIR

# exit when a pipeline does not execute
set -e

# preprocessing
date >> $LOGDIR/status.txt
echo "start PreFreeSurfer pipeline" >> $LOGDIR/status.txt

singularity run -B $OAK:$OAK -B $SCRATCH:$SCRATCH $HCPPIPELINESSINGULARITY $BIDSDIR $PREPDIR participant --participant_label $SUBJECTLABEL --license_key 'CZkaYM9swILM' --n_cpus 8 --stages 'PreFreeSurfer' >> $LOGDIR/prefreesurfer.txt
singularity run -B $OAK:$OAK -B $SCRATCH:$SCRATCH $HCPPIPELINESSINGULARITY $BIDSDIR $PREPDIR participant --participant_label $SUBJECTLABEL --license_key 'CZkaYM9swILM' --n_cpus 8 --stages 'FreeSurfer' >> $LOGDIR/freesurfer.txt
singularity run -B $OAK:$OAK -B $SCRATCH:$SCRATCH $HCPPIPELINESSINGULARITY $BIDSDIR $PREPDIR participant --participant_label $SUBJECTLABEL --license_key 'CZkaYM9swILM' --n_cpus 8 --stages 'PostFreeSurfer' >> $LOGDIR/postfreesurfer.txt
singularity run -B $OAK:$OAK -B $SCRATCH:$SCRATCH $HCPPIPELINESSINGULARITY $BIDSDIR $PREPDIR participant --participant_label $SUBJECTLABEL --license_key 'CZkaYM9swILM' --n_cpus 8 --stages 'fMRIVolume' >> $LOGDIR/volume.txt

date >> $LOGDIR/status.txt
echo "preprocessing finished" >> $LOGDIR/status.txt

# not doing surface processing for now
# date >> $LOGDIR/status.txt
# echo "start fMRISurface pipeline" >> $LOGDIR/status.txt
#$PSYDIR/00_software/HCPPipelines/run.py $BIDSDIR $PREPDIR participant --participant_label $SUBJECTLABEL --license_key 'CZkaYM9swILM' --n_cpus 8 --stages 'fMRISurface' >> $LOGDIR/08_preprocessing_fMRISurface.txt
