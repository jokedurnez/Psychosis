export SUBJECTLABEL=$1
: "${SUBJECTLABEL?ERROR No subjectlabel passed to script...}"

echo "extracting tarfiles"
singularity exec \
    -B $OAK:$OAK \
    -B $SCRATCH:$SCRATCH \
    $CLEANSINGULARITY \
    python $CODEDIR/prebids/bin/scripts/prepare_and_close.py --start

#remove heudiconv directory
HEUDICONVDIR=$BIDSDIR/.heudiconv/$SUBJECTLABEL
if [ -d "$HEUDICONVDIR" ]; then
    rm -rf $HEUDICONVDIR
fi

echo "heudiconv"
singularity run \
    -B $OAK:$OAK \
    -B $SCRATCH:$SCRATCH \
    -c $HEUDICONVSINGULARITY \
    -d $DICOMDIR/{subject}/*/*.dcm \
    -o $BIDSDIR -s $SUBJECTLABEL \
    -f $MISCDIR/heudiconv.py \
    -c dcm2niix

echo "CH-CH-CH-CH-Changes"
singularity exec \
    -B $OAK:$OAK \
    -c $CLEANSINGULARITY \
    python $CODEDIR/prebids/bin/scripts/bids_finish.py

# singularity exec \
#     -B $OAK:$OAK \
#     -B $SCRATCH:$SCRATCH \
#     $CLEANSINGULARITY \
#     python $CODEDIR/01_bids/prepare_and_close.py --start
