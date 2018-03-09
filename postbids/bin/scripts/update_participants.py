'''
    File name: nodes.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 10/31/2017
    Python Version: 2.7
    Description: Script to update participants.tsv with which analyses have been done
    Project: Psychosis
'''

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.environ.get("CODEDIR"))
from postbids.databasing import update_db
from prebids.databasing import psyrc

participants = pd.read_csv(os.path.join(os.environ.get("CLEANTABLE")),sep='\t')

participants = update_db.add_mriqc(participants)

# RC = pd.read_csv(os.environ.get("REDCAPTABLE"),low_memory=False)
# RCcols = [x for sublist in psyrc.redcap_instruments(RC).values() for x in sublist]
# cols = (set(participants.columns) - set(RCcols) - set(['index'])).union(set(['scan_id','subject_id']))
# participants.loc[:,list(cols)]

participants = update_db.check_analyses(participants)
for idx,row in participants.iterrows():
    checks = update_db.check_bids_modalities(row.UID)
    for k,v in checks.iteritems():
        participants.at[idx,k] = v

# check mriqc
bidsincomplete = update_db.check_bids_complete(participants)
update_db.check_analyses_todo(participants)
