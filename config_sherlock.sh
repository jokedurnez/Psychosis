if [ $SHERLOCK = 2 ]
    then
        module load system
        module load singularity/2.4
    fi
if [ $SHERLOCK = 1 ]
    then
        module load singularity
    fi

# DIRECTORIES
export TOPDIR=$OAK/data/Psychosis

export BIDSDIR=$TOPDIR/0.0.3/
export PREPDIR=$BIDSDIR/derivatives/HCPPipelines
export MRIQCDIR=$BIDSDIR/derivatives/MRIQC_0.10.2/
export CONDIR=$BIDSDIR/derivatives/rest_connectome/

export TABLEDIR=$TOPDIR/derivatives/tables/
export MISCDIR=$TOPDIR/derivatives/misc/
export DICOMDIR=$TOPDIR/sourcedata/DICOM/

export CONGROUPDIR=$SCRATCH/Psychosis_derivatives/connectivity_group/
export FIGDIR=$SCRATCH/Psychosis_derivatives/figures/
export MLDIR=$SCRATCH/Psychosis_derivatives/ML/
export HCPDIR=$SCRATCH/psychosis/00_software/Pipelines/

export PSYDIR=$HOME/Psychosis/
export CODEDIR=$PSYDIR

# used singularity containers

export SINGULARITYFOLDER=$PI_HOME/singularity_images/
export HEUDICONVSINGULARITY=$SINGULARITYFOLDER/nipy_heudiconv-2017-08-25-8a97d41632c3.img
export MRIQCSINGULARITY=$SINGULARITYFOLDER/poldracklab_mriqc_0.10.2-2018-02-16-9f22748cdc9a.img
export PALMSINGULARITY=$SINGULARITYFOLDER/joke_palm-2017-04-30-f40670d3ec74.img
export CLEANSINGULARITY=$SINGULARITYFOLDER/joke_psychosis-2017-11-14-281e7efb253a.img
export HCPPIPELINESSINGULARITY=$SINGULARITYFOLDER/joke_hcppipelines_license-2018-03-08-1d1b8ed02ad1.img
## NOTE: joke_hcppipelines_license added the license.txt to /opt/freesurfer to avoid the binding problem in sherlock 1.  If you just take the latest docker from docker hub, the license should be binded to /opt/freesurfer/license.txt

# latest tables
export CLEANTABLE=$BIDSDIR/participants.tsv
export FULLTABLE=$BIDSDIR/derivatives/participants_psychometrics.tsv

export NIDBTABLE=$TABLEDIR/NIDB_03-09-2018.csv
export REDCAPTABLE=$TABLEDIR/REDCAP_201803.csv
export DFTABLE=$TABLEDIR/datafreeze_included_dd07022018.csv
export QCTABLE=$TOPDIR/derivatives/MRIQC_0.9.7/out/mclf_run-20171110-171555_data-unseen_pred.csv

export GORDONLABELS=$TABLEDIR/Gordon_labels.csv
export CEREBELLUMLABELS=$TABLEDIR/Cerebellum_labels.csv
export SUBCORTLABELS=$TABLEDIR/Subcort_labels.csv
export ATLASLABELS=$TABLEDIR/Atlas_labels.csv

export EXCLUSIONTABLE=$TABLEDIR/exclude.json
export EXCLUSION_NIDB=$CODEDIR/prebids/databasing/exclusion_NIDB.json
export EXCLUSION=$CODEDIR/prebids/databasing/exclusion_rules.json
