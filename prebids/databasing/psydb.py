'''
    File name: psydb.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 10/31/2017
    Python Version: 2.7
    Description: Script to clean up NIDB
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

with open(os.environ.get("EXCLUSION_NIDB"),'r') as fl:
    rules = json.load(fl)

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
    for rule in rules:
        if rule['reason'] == 'typo':
            for k,v in rule['pairs'].iteritems():
                DB.AltStudyID[DB.AltStudyID==k] = v
        else:
            for idx,sub in enumerate(rule['remove']):
                DB = DB[DB.UID!=sub]
    return DB

def clean_DB(DB):
    print("============= Cleaning NIDB database ==============")
    DB = remove_old(DB)
    DB = unique_subs(DB)
    DB = remove_spaces(DB)
    DB = database_exclude(DB)
    DB = DB.drop_duplicates()
    DB = DB.reset_index()
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
