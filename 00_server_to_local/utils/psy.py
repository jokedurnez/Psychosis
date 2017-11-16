'''
    File name: psy.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 10/31/2017
    Python Version: 2.7
    Description: Script to clean up database
    Project: Psychosis
'''

import pandas as pd
import os
import shutil
from distutils.dir_util import copy_tree
import numpy as np
import json
import csv
from datetime import datetime
import collections
from collections import Counter

def handle_repeated_scans(PSYDB,EXDB):
    print("============= Checking potential reasons for exclusion ==============")
    for idx,row in PSYDB.iterrows():
        note = row.if_there_are_repeated_scan
        if not (pd.isnull(note)):
            exid = np.where(row.scan_id == EXDB.scan_id)[0]
            if len(exid)>0:
                if list(EXDB.exclude[exid])[0]==False:
                    PSYDB = PSYDB.set_value(idx,'exclude',0)
                    continue
                else:
                    PSYDB = PSYDB.set_value(idx,'exclude',1)
                    if list(EXDB.action[exid])[0]=='not handled yet':
                        print("    --Check the message in subject %s - %s - database id %i: %s"%(row.subject_id,row.scan_id,idx,row.if_there_are_repeated_scan))
                        print("       Add a note to $EXCLUSIONTABLE when dealt with.")
            else:
                if row.in_nidb==1:
                    newline = {
                        "RC_id":row.subject_id,
                        "UID":row.UID,
                        "action":"not handled yet",
                        "exclude":True,
                        "note":row.if_there_are_repeated_scan,
                        "scan_id":row.scan_id
                    }
                    PSYDB = PSYDB.set_value(idx,'exclude',0)
                    print("add %s to exfile"%str(newline))
                    EXDB.append(newline,ignore_index=True)
    return PSYDB,EXDB

def exclude_incomplete(PSYDB,EXDB):
    for idx,row in EXDB.iterrows():
        if row.action=='incomplete':
            dbid = np.where(row.UID==PSYDB.UID)[0][0]
            PSYDB = PSYDB.set_value(dbid,'exclude',1)

    return PSYDB,EXDB

def add_freeze(PSYDB,DF):
    print("============= Checking data freeze ==============")
    PSYDB['datafreeze']=0
    for idx,row in PSYDB.iterrows():
        if row.subject_id in DF:
            PSYDB = PSYDB.set_value(idx,'datafreeze',1)
    print("   at this point %i subjects are included in the datafreeze"%(Counter(PSYDB.datafreeze)[1]))
    return PSYDB
