# check subjectlabel

export SUBJECTLABEL=$1
: "${SUBJECTLABEL?ERROR No subjectlabel passed to script...}"

# dicom to bids
date
echo "started conversion from dicom to nii in bids"

export PYTHONPATH=""
singularity exec $HEUDICONVSINGULARITY echo 'Singularity container loaded.'

singularity run -B $OAK:$OAK -B $SCRATCH:$SCRATCH -c $HEUDICONVSINGULARITY -d $DICOMDIR/{subject}/*/*.dcm -o $BIDSDIR -s $SUBJECTLABEL -f $MISCDIR/heudiconv.py -c dcm2niix

# make bidsdir writeable
chmod -R 750 $BIDSDIR/$SUBJECTLABEL

# manual approach to certain subjects with certain specs
singularity exec -B $OAK:$OAK -B $HOME:$HOME -c $HEUDICONVSINGULARITY python $CODEDIR/01_bids/manual.py

# write json's for bids-specification compliance
# singularity exec -B $OAK:$OAK -B $HOME:$HOME -c $HEUDICONVSINGULARITY python $CODEDIR/01_bids/bids_add_fields.py

# concatenate the fieldmaps per direction
date
echo "concatenate fieldmaps"

FDIR=$BIDSDIR/sub-$SUBJECTLABEL/fmap/
if [ -d "$FDIR" ]; then
  # Control will enter here if $DIRECTORY doesn't exist
    fmap_dir1=$(ls $BIDSDIR/sub-$SUBJECTLABEL/fmap/sub-$SUBJECTLABEL\_dir-1_*epi.nii.gz)
    singularity exec -B $OAK:$OAK $MRIQCSINGULARITY fslmerge -t $BIDSDIR/sub-$SUBJECTLABEL/fmap/sub-$SUBJECTLABEL\_dir-1_epi.nii.gz $fmap_dir1
    cp $BIDSDIR/sub-$SUBJECTLABEL/fmap/sub-$SUBJECTLABEL\_dir-1_run-1_epi.json $BIDSDIR/sub-$SUBJECTLABEL/fmap/sub-$SUBJECTLABEL\_dir-1_epi.json

    fmap_dir2=$(ls $BIDSDIR/sub-$SUBJECTLABEL/fmap/sub-$SUBJECTLABEL\_dir-2_*epi.nii.gz)
    singularity exec -B $OAK:$OAK $MRIQCSINGULARITY fslmerge -t $BIDSDIR/sub-$SUBJECTLABEL/fmap/sub-$SUBJECTLABEL\_dir-2_epi.nii.gz $fmap_dir2
    cp $BIDSDIR/sub-$SUBJECTLABEL/fmap/sub-$SUBJECTLABEL\_dir-2_run-1_epi.json $BIDSDIR/sub-$SUBJECTLABEL/fmap/sub-$SUBJECTLABEL\_dir-2_epi.json

    rm -rf $BIDSDIR/sub-$SUBJECTLABEL/fmap/sub-$SUBJECTLABEL\_*run-*
fi

date
echo "finished pipeline"
