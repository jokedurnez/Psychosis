if [ $SHERLOCK = 2 ]
    then
        module load system
        module load singularity/2.4
    fi
if [ $SHERLOCK = 1 ]
    then
        module load singularity
#        source /share/PI/russpold/software/setup_all.sh
    fi

# DIRECTORIES
export TOPDIR=$OAK/data/Psychosis
export BIDSDIR=$TOPDIR/0.0.1/
export PREPDIR=$TOPDIR/derivatives/HCPPipelines/
export MRIQCDIR=$TOPDIR/derivatives/MRIQC_0.9.7/
export TABLEDIR=$TOPDIR/derivatives/tables/
export MISCDIR=$TOPDIR/derivatives/misc/
export DICOMDIR=$TOPDIR/sourcedata/DICOM/
export CONDIR=$TOPDIR/derivatives/rsfMRI_processed/

export CLEANTABLE=$BIDSDIR/participants.csv

export CONGROUPDIR=$SCRATCH/Psychosis_derivatives/connectivity_group/
export FIGDIR=$SCRATCH/Psychosis_derivatives/figures/
export MLDIR=$SCRATCH/Psychosis_derivatives/ML/

export PSYDIR=$HOME/Psychosis/
export CODEDIR=$PSYDIR

# used singularity containers
export SINGULARITYFOLDER=$PI_HOME/singularity_images/
export HEUDICONVSINGULARITY=$SINGULARITYFOLDER/nipy_heudiconv-2017-08-25-8a97d41632c3.img
export HCPPIPELINESSINGULARITY=$SINGULARITYFOLDER/joke_hcppipelines-2017-11-06-021357a6e390.img
export FMRIPREPSINGULARITY=$SINGULARITYFOLDER/poldracklab_fmriprep_1.0.0-rc9-2017-11-03-f95527bc7669.img
export MRIQCSINGULARITY=/share/PI/russpold/singularity_images/poldracklab_mriqc_0.9.7-rc5-2017-07-20-390ff3254851.img
export PALMSINGULARITY=$SINGULARITYFOLDER/joke_palm-2017-04-30-f40670d3ec74.img
export PANDASSINGULARITY=$SINGULARITYFOLDER/toast38coza_python27-pandas-2016-02-18-3a9f3fab0a4c.img
export CLEANSINGULARITY=$SINGULARITYFOLDER/joke_psychosis-2017-11-14-281e7efb253a.img

# latest tables

export NIDBTABLE=$TABLEDIR/NIDB_10-31-2017.csv
export NIDBcleanTABLE=$TABLEDIR/NIDB_clean.csv

export DATABASE=$TABLEDIR/DATABASE.csv
export REDCAPTABLE=$TABLEDIR/REDCAP_201710.csv
export EXCLUSIONTABLE=$TABLEDIR/exclude.json

export GORDONLABELS=$TABLEDIR/Gordon_labels.csv
export CEREBELLUMLABELS=$TABLEDIR/Cerebellum_labels.csv
export SUBCORTLABELS=$TABLEDIR/Subcort_labels.csv
export ATLASLABELS=$TABLEDIR/Atlas_labels.csv
