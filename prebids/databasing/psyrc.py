#!/usr/bin/env python

'''
    File name: psyrc.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 02/08/2018
    Python Version: 2.7
    Description: Script to clean up redcap
    Project: Psychosis
'''

from distutils.dir_util import copy_tree
from collections import Counter
from datetime import datetime
import pandas as pd
import numpy as np
import collections
import shutil
import json
import csv
import os

def redcap_subset(RC):
    print("    ...subsetting redcap (1 line per subject, only completed mri, not dropped)...")
    #subset consensus line
    RC = RC[RC.subject_id.str.len()==4]
    RC.reset_index(inplace=True,drop=True)
    return RC

def redcap_instruments(RC):
    print("    ...getting redcap instruments...")
    # extract and organise redcap variables
    RC_instruments = {
        "subject_status": RC.columns.values[:12].tolist(),
        "health_screening": RC.columns.values[12:130].tolist(),
        "legal_issues": RC.columns.values[130:203].tolist(),
        "wasi_2scale": RC.columns.values[203:211].tolist(),
        "bprse": RC.columns.values[211:238].tolist(),
        "hamd": RC.columns.values[238:263].tolist(),
        "ymrs": RC.columns.values[263:277].tolist(),
        "ldps_c26a": RC.columns.values[277:346].tolist(),
        "family_history_assessment": RC.columns.values[346:624].tolist(),
        "ctq": RC.columns.values[624:654].tolist(),
        'THQ': RC.columns.values[654:746].tolist(),
        "mri": RC.columns.values[746:777].tolist(),
        "scid": RC.columns.values[777:803].tolist(),
        "scid_face_page": RC.columns.values[803:825].tolist(),
        "scid_axis_diagnosis": RC.columns.values[825:849].tolist()
    }
    return RC_instruments

def redcap_fix_typos(RC):
    print("    ...fixing typo's...")
    # see Imaging_dataabse_summary_03242017 - ADO-Redcap discrepancy
    RC.at[RC.scan_id=='S3402BBF','scan_id']='S3402BFF'
    RC.at[RC.scan_id=='S7191EIM','scan_id']='S719EIM'
    RC.at[RC.scan_id=='S7854VNC','scan_id']='S7854NC'
    RC.at[RC.scan_id=='S9630QVW','scan_id']='S4630QVW'
    # see Imaging_dataabse_summary_03242017 - Joke Questions Addressed
    RC.at[RC.scan_id=='S5833EJE','scan_id']='S5833ESE'
    # the \t that is in the original file screws up bids-validator
    # -> could maybe be improved with automatic replacement,
    # but will take extra CPU than manually inspecting from time to time
    RC.at[RC.scan_id=='S8002CQJ',"medication_2"]="Norvasc, anti-hypertensive, unknown dose, 1x - Prolixin, typical antipsychotic, unknown dose, 2x"
    RC.at[RC.scan_id=='S3581IVG',"primary_diagnosis_code"]="305"
    RC.at[RC.scan_id=='S7178SLQ',"medication_3"]="Gabapentin, side effect control/Anticonvulsant, 300mg, PRN"
    RC.at[RC.scan_id=='S8112DPT',"medication_5"]="Lansoprazole, acid reflux, unknown dose, 1x"
    return RC

def clean_RC(RC):
    print("============= Cleaning RedCap database ==============")
    RC = redcap_subset(RC)
    RC = redcap_fix_typos(RC)

    return RC

def redcap_merge(PSYDB,RC):
    print("============= Merging RedCap in database ==============")
    RC_col = redcap_instruments(RC)
    RC_col = [x for sublist in RC_col.values() for x in sublist]
    numbers = {"present":0,'nidb_only':0,'new':0}
    print("    ...looping over all entries...")
    for idx,row in RC.iterrows():

        ########## SITUATION 1: subject found by redcap identifier ###########
        if not pd.isnull(row.subject_id) and row.subject_id in list(PSYDB.subject_id.values):
            # check index
            PSYDBid = np.where(PSYDB.subject_id==row.subject_id)[0][0]
            # check if everything reccap specificis equal
            eq = PSYDB.loc[PSYDBid,RC_col].equals(row[RC_col])
            if eq:
                # no action
                numbers['present']+=1
            else:
                # print warning
                print("Subject %s already in psydb, but not matching redcap. Please check. Skipping now."%(row.subject_id))

        ########## SITUATION 2: subject not in redcap, but in nidb ###########
        elif not pd.isnull(row.scan_id) and row.scan_id in PSYDB.scan_id.values:
            # get index
            PSYDBid = np.where(PSYDB.scan_id==row.scan_id)[0][0]
            numbers['nidb_only']+=1
            # prepare to fill out missing
            newsub = dict(row)
            newsub['in_redcap']=True
            # fill out values
            PSYDB.loc[PSYDBid,newsub.keys()]=newsub.values()

        ########## SITUATION 3: completely new subject ###########
        else:
                numbers['new']+=1
                newsub = dict(row)
                newsub['in_redcap']=True
                PSYDB = PSYDB.append(newsub,ignore_index=True)

    print("    added %i new subjects; %i subjects were already present in NIDB"%(numbers['new'],numbers['nidb_only']))
    return PSYDB
