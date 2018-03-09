'''
    File name: 00_generate_database.py
    Author: Joke Durnez
    Date created: 02/13/2018
    Date last modified: 02/13/2018
    Python Version: 2.7
    Description: Script to create database for psychosis project
    Project: Psychosis
'''

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.environ.get("CODEDIR"))
pd.options.mode.chained_assignment = None  # default='warn'

from prebids.databasing import psyrc, psydb, psy, exclude

# clean different tables
DB = pd.read_csv(os.environ.get("NIDBTABLE"))
DB = psydb.clean_DB(DB)
RC = pd.read_csv(os.environ.get("REDCAPTABLE"),low_memory=False)
RC = psyrc.clean_RC(RC)
cols = psyrc.redcap_instruments(RC)

# initiate big database
cols = psyrc.redcap_instruments(RC)
cols = [x for sublist in cols.values() for x in sublist]
cols += ['UID','in_redcap','in_nidb','exclude']
PSYDB = pd.DataFrame({x:[] if not x =='UID' else "" for x in cols})

# merge in redcap and nidb
PSYDB = psydb.nidb_merge(PSYDB,DB)
PSYDB.fillna(value={'in_nidb':False})
PSYDB = psyrc.redcap_merge(PSYDB,RC)

# deal with excluded subjects
EX = exclude.instantiate_exclusion_table(DB,RC)
EXDB = pd.DataFrame(EX)
PSYDB,EXDB = psy.exclude_incomplete(PSYDB,EXDB)

# add freeze column
PSYDB = psy.add_freeze(PSYDB)
print("Total subjects not in freeze: %i"%len(PSYDB))

# get subset
SUBSET = PSYDB[PSYDB.datafreeze==1]
print("Total subjects in freeze: %i"%len(SUBSET))
#subset complete
SUBSET = SUBSET[SUBSET.subject_status_complete==2]
print("Total subjects complete: %i"%len(SUBSET))
#subset MRI finished
SUBSET = SUBSET[SUBSET.is_this_subject_a_patient!=0]
print("Total subjects not dropped: %i"%len(SUBSET))
#subset MRI available
SUBSET = SUBSET[SUBSET.in_nidb==1]
print("Total subjects in NIDB: %i"%len(SUBSET))
#subset MRI available
SUBSET = SUBSET[SUBSET.exclude!=1]
print("Total subjects after exclusions: %i"%len(SUBSET))

SUBSET = SUBSET.reset_index(drop=True)

# add participant_id to columns
SUBSET['participant_id'] = ['sub-%s'%x for x in SUBSET.UID]
# SUBSET = SUBSET.drop('UID',axis=1)
# SUBSET = SUBSET.drop('scan_id',axis=1)

SUBSET = SUBSET.fillna("n/a")
SUBSET.to_csv(os.environ.get("FULLTABLE"),sep="\t",index=False)

SUBSET = SUBSET[['subject_id','participant_id','is_this_subject_a_patient','UID']]
SUBSET.to_csv(os.environ.get("CLEANTABLE"),sep="\t",index=False)
