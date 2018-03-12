#!/usr/bin/env python

'''
    File name: database.py
    Author: Joke Durnez
    Date created: 02/08/2018
    Date last modified: 02/08/2018
    Python Version: 2.7
    Description: Functions to deal with database
    Project: Psychosis
'''

import pandas as pd
import numpy as np
import json
import sys
import os

sys.path.append(os.environ.get("CODEDIR"))
from prebids.databasing import psyrc, psydb

def initiate_exclusion_table(DB,RC):
    # get tables
    EXDB = []
    for idx,row in DB.iterrows():
        # loop over DB: only look at scans in DB
        RCid = np.where(row.AltStudyID==RC.scan_id)[0]
        if len(RCid)==0:
            continue
            # if not in RC: ignore
        note = RC.if_there_are_repeated_scan[RCid[0]]
        if (type(note)==str and len(note)>0):
            adrow = {
                "note":note,
                "exclude":True,
                "scan_id":row.AltStudyID,
                "RC_id":RC.subject_id[RCid[0]],
                "UID":row.UID,
                "action":"not handled yet",
                'inspected':False
            }
            EXDB.append(adrow)
    return EXDB

def instantiate_exclusion_table(DB,RC):
    EXDB = initiate_exclusion_table(DB,RC)
    EXDB = pd.DataFrame(EXDB)
    with open(os.environ.get("EXCLUSION"),'r') as fl:
        rules = json.load(fl)
    for issue in rules:
        for sub in issue['subjects']:
                if sub not in list(DB.UID):
                    print("subject %s not in DB"%sub)
                    continue
                subid = np.where(EXDB.UID==sub)[0]
                DBid = np.where(DB.UID==sub)[0][0]
                RCid = np.where(sub==RC.scan_id)[0]
                if len(subid)==0:
                    newrow = {
                        "action"
                    }
                EXDB.at[subid,'action'] = issue['problem']
                EXDB.at[subid,'exclude'] = issue['exclude']
                EXDB.at[subid,'inspected'] = True
    EXDB = EXDB.T.to_dict().values()
    with open(os.environ.get("EXCLUSIONTABLE"),'w') as fl:
        json.dump(EXDB,fl)
    return EXDB
