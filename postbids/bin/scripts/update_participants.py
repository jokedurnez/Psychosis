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
#participants['MRIQC_score']=0

# check which folders exist
participants = update_db.check_analyses(participants)
for idx,row in participants.iterrows():
    # add to db which modalities exist
    checks = update_db.check_bids_modalities(row.UID)
    for k,v in checks.iteritems():
        participants.at[idx,k] = v

# check if all bids is complete
bidsincomplete = update_db.check_bids_complete(participants)
# check which analyses should be done
out = update_db.check_analyses_todo(participants)

participants = participants.reset_index(drop=True)
participants = participants.fillna("n/a")
participants.to_csv(os.environ.get("CLEANTABLE"),sep="\t",index=False)
