'''
    File name: psy.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 10/31/2017
    Python Version: 2.7
    Description: Script to clean up database
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

def exclude_incomplete(PSYDB,EXDB):
    for idx,row in EXDB.iterrows():
        if row.exclude==True:
            dbid = np.where(row.UID==PSYDB.UID)[0][0]
            PSYDB.at[dbid,'exclude']=1
        return PSYDB,EXDB

def add_freeze(PSYDB):
    print("============= Checking data freeze ==============")
    DF_file = os.environ.get("DFTABLE")
    DF = pd.read_csv(DF_file)
    PSYDB['datafreeze']=0
    for idx,row in PSYDB.iterrows():
        if not isinstance(row.subject_id,str):
            continue
        ind = np.where(int(row.subject_id)==np.array(DF['Subject ID']))[0]
        if len(ind)>0:
            status = DF.at[ind[0],'Subject Status']
            if status=='Complete' and isinstance(DF.at[ind[0],'Scan ID alt (NIDB)'],str):
                PSYDB.at[idx,'datafreeze']=1
    print("   at this point %i subjects are included in the datafreeze"%(Counter(PSYDB.datafreeze)[1]))
    return PSYDB
