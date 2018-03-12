# Psychosis project

## Analysis protocol pre-bids

All data and analyses are on sherlock.  In the main directory, there is a file `config_sherlock.sh`.  Sourcing that file will set environment variables used throughout the scripts.

### 0. Initiate project

If the Bids directory is not existing or empty, run first `$CODEDIR/prebids/scripts/00_generate_bids_folder.py`

### 1. GET data

In the first step, we get the data in BIDS format.

**1. On OLIN NIDB, find current content**:
* project: AA Connectivity
* results: Summary in spreadsheet
* Download file to 09\* and rename to NIDB_mo-da-year.csv
* Change the location of `$NIDBTABLE` in `config_sherlock.sh` and rerun
* Remove last column of csv (will give errors when reading in pandas)

**2. On REDCAP, find current content**
* Download from Redcap all the data, and rename and move to `$TABLEDIR/REDCAP_YearMo.csv`
* Change the name/location of `$REDCAPTABLE` in `config_sherlock.sh`
* Note: it sometimes happens that the columns from redcap change, be careful.

**3. Generate database**

  * Run `$CODEDIR/prebids/scripts/01_generate_database.py` to generate the new database and to see which subjects should be downloaded and/or bidsified.
  * for missing subjects on sherlock:
    - search subject ID's in database (UIDs), results in 'Series List', separated with comma's.  Not too many at a time: might take a really long time to zip/download
    - select all files
    - Download:
        - type: web
        - data: all
        - format: DICOM, no anonymization, gzip files
        - directory format: study ID
        - series directories: use protocol name
        - behavioral data: place in beh directory in root
    - To download:
        - Check the download link on the database
        - Run the following in an interactive session:

                    cd $DICOMDIR/import
                    wget http://olinnidb.org/download/NIDB-1636.zip
                        (replace with download link)

            (I wrote a script earlier, but the download slowed down after a while and timed out, so it's better to do it in an interactive session)
        - Run `$CODEDIR/prebids/dicom/dicom.import_newdata()` to organise the new data where they should be.


  * Check if all the available data are on sherlock: TO DO
<!-- Run `00*/check_complete_subjects`.  This will notifiy if there is an incomplete overlap between sherlock and NIDB.  I've ignored those warnings for DTI scans or localisers as we don't use these.  The program also checks if there are subjects who don't have all of our protocols.  This should be redone. -->


**4. Check exclusions**

* After the previous step, a database (stored in `$CLEANTABLE`) is generated.  What needs to be checked first:
    - Check which subjects are excluded from the cleantable.  Normally generating the cleantable will give a warning if there are subjects not handled.  Look at `$EXCLUSIONTABLE`.  This table has two types of subjects:
        1. The ones who had a note in redcap.  Constructing the database automatically excludes everyone with a note and places them in the exclusiontable, since these could indicate a problem.
        2. Incompletes.  If certain subjects don't have an entry for certain paradigms (like anatomicals), they will be excluded too.
    - All subjects that are placed in the exclusiontable should be inspected manually, and a rule should be added to `$CODEDIR/prebids/databasing/exclusion_rules.json`.  This file will be read during bidsifying, so pay attention to syntax.
    These are a few heuristics I've used to decide how to deal with notes:
    - There is a list of protocols that we use for our analyses: the resting state sessions, the fieldmaps and the anatomical.  Basically, if the error or problem is with another scan, I ignore this warning.  
    - If one of these scans we use have been repeated for one or another reason, the scans are checked.  If the second is better, the first is discarded.
    - If we don't have at least T1 and T2, the subject is excluded.

One very useful tool to figure out what happened is in the python library: `prebids.dicom.get_timetable(UID)`.  This will give a timetable of the different scans.  Very useful to get insight in when a subject left the scanner or which scans have been repeated at what point.

### 1. Do Bids

Bidsifying is now just a matter of running BidsSLURM.sh in an array job, with the array numbers 0-X, with X the length of participants.tsv

**Note**:
- I have completely ignored the HCP task warnings.  This should be handled at some point !
- Bidsifying S1318RPT was damn hard, since it was in two sessions and our setup is not prepared for that :-).  (I also didn't want 1 subject with two sessions. That would screw up all further analyses assuming 1 session per subject.  How I solved it:
    * keep two sessions as two separate 'subjects' for heudiconv
            export SUBJECTLABEL=S1318RPT1
            singularity run \
            -B $OAK:$OAK \
            -B $SCRATCH:$SCRATCH \
            -c $HEUDICONVSINGULARITY \
            -d $DICOMDIR/{subject}/*/*.dcm \
            -o $BIDSDIR -s $SUBJECTLABEL \
            -f $MISCDIR/heudiconv.py \
            -c dcm2niix

            export SUBJECTLABEL=S1318RPT2
            singularity run \
            -B $OAK:$OAK \
            -B $SCRATCH:$SCRATCH \
            -c $HEUDICONVSINGULARITY \
            -d $DICOMDIR/{subject}/*/*.dcm \
            -o $BIDSDIR -s $SUBJECTLABEL \
            -f $MISCDIR/heudiconv.py \
            -c dcm2niix
    * run prebids/bin/scripts/XX_combine_S1318RPT
    * set the right SUBJECTLABEL
            export SUBJECTLABEL=S1318RPT
    * run prebids/bin/scripts/bids_finish.py (maybe manually only the exclusions)
