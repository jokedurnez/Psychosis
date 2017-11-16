# Psychosis project

## Principled approach to Psychosis Data

### data structure

All data and analyses are on sherlock.  In the main directory, there is a file `config_sherlock.sh`.  Sourcing that file will set environment variables used throughout the scripts.

There is a database that collects information about analyses, sessions, problems,... in environment variable `DATABASE`.  There is another database (environment var `CLEANTABLE`) which is a subset of `DATABASE` containing subjects ready for analysis.

### 1. GET DATA

In the first step, we get the data in BIDS format.

**1. On OLIN NIDB, find current content**:
  * project: AA Connectivity
  * results: Summary in spreadsheet
  * Download file to 09\* and rename to NIDB_mo-da-year.csv
  * Change the location of `$NIDBTABLE` in `config_sherlock.sh` and rerun
  * Remove last column of csv (will give errors when reading in pandas)


**2. Clean the database and check for new subjects**
  * Run `$CODEDIR/00_server_to_local/clean_NIDB.py` to clean the new database and to see which subjects should be downloaded and/or bidsified.
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
                    wget http://olinnidb.org/download/NIDB-1380.zip
                        (replace with download link)

            (I wrote a script earlier, but the download slowed down after a while and timed out, so it's better to do it in an interactive session)
        - Run `01*/00*/00_extract_and_organise.sh`: this script will extract the zipfiles and put them in the dicomdir.


  * Check if all the available data are on sherlock
         Run `00*/check_complete_subjects`.  This will notifiy if there is an incomplete overlap between sherlock and NIDB.  I've ignored those warnings for DTI scans or localisers as we don't use these.  The program also checks if there are subjects who don't have all of our protocols.

**3. On REDCAP, find current content**
  * Download from Redcap all the data, and rename and move to `$TABLEDIR/REDCAP_YearMo.csv`
  * Change the name/location of `$REDCAPTABLE` in `config_sherlock.sh`


**4. Combine tables in database**

Run `00*/database.py`: This adds these tables to the database (or creates the database from scratch). This will check different things:

  - *Check for repeated scans:*
    * There is an entry in redcap that states if and when subjects had a problematic session: we need to manually check what the error was and what to do with that.  A few rules I've implemented:
        - There is a list of protocols that we use for our analyses: the resting state sessions, the fieldmaps and the anatomical.  Basically, if the error or problem is with another scan, I ignore this warning.  
        - If one of these scans we use have been repeated for one or another reason, the scans are checked.  If the second is better, the first is discarded.
        - If we don't have at least 2 resting state sessions (RL + LR), T1 and T2, the subject is excluded.
    * We have an exclusion table (see config file), which is a json with all problematic files of incomplete subjects.  Running database.py will notify if any problems haven't been handled (those are automatically excluded).  To 'handle' the issue, add a note in this exclusionfile (and if necessary, add a rule to manual.py in the bids folder in case something needs to change to the scans)

**5. Check which analyses are missing**

After running `00*/database.py`, there are columns `con`, `mriqc`, `prep` and `bids`.  These columns indicate whether these steps have been run.  If they are not run, submit these jobs as below.

### 2. ANALYSIS PIPELINE

All analyses will happen based on the cleaned database.  We can now run each analysis pipeline, for each subject in the database.
The flow:
1. the pipelines use the subject ID as input
2. we use array jobs, where the array ID corresponds to the index of the subject in the database

##### 1. bidsify images in database

- After checking which subjects should be analysed (see up), run the following command:

        sbatch --output=$CODEDIR/01_bids/logs/bids_%a.out \
            --error=$CODEDIR/01_bids/logs/bids_%a.err \
            --export=ALL \
            --job-name=PSY_BIDS \
            --array=0-198 \
            -N1 $CODEDIR/01_bids/BidsSLURM.sh

This will run the pipeline for subjects with indices 1-199.  To run only a few specific subjects, change for example to `--array=1,2` to run indices 1 and 2.
- A few subjects require specific handling (see 2.2), these changes are handled in `manual.py`
- The table that is used for bidsifying is the NIDB-table (and not the clean database).  The reason is that it is sometimes necessary to look ad the bids'ed data, so we want more data bidsified than we will ultimately analyse.  If there are subjects that shouldn't be bidsified after all (excluded) then these data should be removed later.

##### 2. MRIQC

- After finishing bidsifying, you can run MRIQC
- Takes about 40 minutes per subject

        sbatch --output=$CODEDIR/02_mriqc/logs/MRIQC_%a.out \
            --error=$CODEDIR/02_mriqc/logs/MRIQC_%a.err \
            --export=ALL \
            --job-name=PSY_QC \
            --array=0-200 \
            -N1 $CODEDIR/02_mriqc/MriQCSLURM.sh


##### 3. preprocessing

- Can be run in parallel with MRIQC (after bidsifying)
- Takes about 20-25 hours per subject
- Analysis of surface (fMRISurface) is commented out as we're not using that for now, same for DWI.
- To submit, run:

        sbatch --output=$CODEDIR/03_preprocessing/logs/PREP_%a.out \
            --error=$CODEDIR/03_preprocessing/logs/PREP_%a.err \
            --export=ALL \
            --job-name=PSY_PREP \
            --array=0-198 \
            -N1 $CODEDIR/03_preprocessing/PreProcessingSLURM.sh

- Note: in `PREPDIR/S*/task-*`, the preprocessing generates a HUGE amount of datafiles, which messes up our limits.  For that reason, these folders have been tarred using `01*/misc/preproc_tar.sh`.  It would be probably a good idea to re-run this script after new data have been preprocessed.

#### 6. time series cleaning / connectome

- Cleans timeseries and creates connectomes for each subject.
- To submit, run:

        sbatch --output=$CODEDIR/04_connectome/01_timeseries_cleaning/logs/CLEAN_%a.out \
            --error=$CODEDIR/04_connectome/01_timeseries_cleaning/logs/CLEAN_%a.err \
            --export=ALL \
            --job-name=PSY_CLEAN \
            --array=0-198 \
            -N1 $CODEDIR/04_connectome/01_timeseries_cleaning/CleaningSLURM.sh


#### 7. connectome_group
To do
<!-- - Up until now, all tasks could be run in parallel, one for each subject.  Here the connectomes are combined.
- First run `combine_all.py`, which makes a table and numpy files with all data combined
- Next, `stattestSLURM`, calling `stattest.py`, should be run, which performs statistical inference (multilevel of course) on the connectomes.  This runs 333 jobs: one for each column in the Gordon parcellation.
- Then `export.py` exports the data to the format read by the shiny application.
- `plt_example.py` makes the figures showing the time series for one subject (subject ID in script) -->

#### misc
- There is a folder with miscellaneous scripts.  I'll annotate them one day.
