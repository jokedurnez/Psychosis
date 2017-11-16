'''
    File name: psydb.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 10/31/2017
    Python Version: 2.7
    Description: Script to clean up NIDB
    Project: Psychosis
'''

from collections import Counter
import pandas as pd
import os
import shutil
from distutils.dir_util import copy_tree
import numpy as np
import json
import csv
from datetime import datetime

def remove_old(DB):
    #from DB file: remove old subjects from other study
    print("    ...removing subjects from before 2015...")
    new_id = [id for id,val in enumerate(DB[' study type']) if datetime.strptime(val,' %Y-%m-%d %H:%M').year>=2015]
    DB = DB.loc[new_id]
    return DB

def unique_subs(DB):
    print("    ...extracting subjects...")
    DB = DB[[' UID',' AltStudyID',' Study date',' Sex']]
    DB = DB.drop_duplicates()
    return DB

def remove_spaces(DB,protocols=False):
    print("    ...removing spaces in names...")
    scanID = [x[1:] for x in DB[' UID'].tolist()]
    behID = [x[1:] for x in DB[' AltStudyID'].tolist()]
    out = {"UID":scanID, "AltStudyID":behID}
    if protocols:
        protocol = [x[1:] for x in DB[' Protocol'].tolist()]
        out["Protocol"] = protocol
    DB = pd.DataFrame(out)
    return DB

def database_exclude(DB):
    print("    ...removing double subjects...")
    # remove doubles (has to be before merge with db)
    goners =  ['S7510LXD', 'S3601YYJ', 'S1778LHR', 'S9001JIS', 'S2600PKA', 'S3690RHU', 'S2073HRA', 'S6263LCT','S3540EUP','S7455FRR']
    keepers = ['S6086STG', 'S7525VYE', 'S2531WXG', 'S9650KBD', 'S7795BWP', 'S2673YWR', 'S8848XEU', 'S0784SQF','S0896XRN','S1516JWK']
    for idx,sub in enumerate(goners):
        DB = DB[DB.UID!=sub]
    print("    ...fixing typo's...")
    if '663' in list(DB.AltStudyID):
        # subject with AltID = 4663: should be S3581IVG (is known on DB as S6020APK)
        DB.AltStudyID[DB.AltStudyID=='663'] = 'S3581IVG'
    return DB

def clean_DB(DB):
    print("============= Cleaning NIDB database ==============")
    DB = remove_old(DB)
    DB = unique_subs(DB)
    DB = remove_spaces(DB)
    DB = database_exclude(DB)
    DB = DB.drop_duplicates()
    return DB

def nidb_merge(PSYDB,DB):
    print("============= Merging NIDB in database ==============")
    DB = DB.rename(columns = {"AltStudyID":"scan_id"})
    DB_col = DB.columns
    numbers = {"present":0,'redcap_only':0,'new':0}
    print("    ...looping over all entries...")
    for idx,row in DB.iterrows():
        newsub = dict(row)
        newsub['in_nidb']=True
        PSYDB = PSYDB.append(newsub,ignore_index=True)

    print("added %i new subjects"%len(PSYDB))
    return PSYDB
