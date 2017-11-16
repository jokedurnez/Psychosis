from collections import Counter
import pandas as pd
import os
import shutil
from distutils.dir_util import copy_tree
import numpy as np
import json
import csv
import sys
from datetime import datetime
from pandas.util.testing import assert_frame_equal
import utils.psydb as psydb
import utils.psyrc as psyrc
import utils.psy as psy

# read in redcap and nidb
DB = pd.read_csv(os.environ.get("NIDBcleanTABLE"))
RC = pd.read_csv(os.environ.get("REDCAPTABLE"),low_memory=False)
RC = psyrc.clean_RC(RC)

cols = psyrc.redcap_instruments(RC)
cols = [x for sublist in cols.values() for x in sublist]
cols += ['UID','in_redcap','in_nidb','exclude']
PSYDB = pd.DataFrame({x:[] if not x =='UID' else "" for x in cols})

# combine nidb and redcap in database
PSYDB = psydb.nidb_merge(PSYDB,DB)
PSYDB = psyrc.redcap_merge(PSYDB,RC)

with open(os.environ.get("EXCLUSIONTABLE"),'r') as fl:
    data = json.load(fl)

EXDB = pd.DataFrame(data)

PSYDB,EXDB = psy.handle_repeated_scans(PSYDB,EXDB)
PSYDB,EXDB = psy.exclude_incomplete(PSYDB,EXDB)

EXDB = EXDB.T.to_dict().values()
with open(os.environ.get("EXCLUSIONTABLE"),'w') as fl:
    json.dump(EXDB,fl)

# make variable on datafreeze
DF_file = os.path.join(os.environ.get("TABLEDIR"),"datafreeze.xlsx")
DF = pd.read_excel(DF_file)
DF = [str(x) for x in DF['Subject ID']]
PSYDB = psy.add_freeze(PSYDB,DF)

# add mriqc
table = os.path.join(os.environ.get("MRIQCDIR"),'out/mclf_run-20171110-171555_data-unseen_pred.csv')
generalisation = pd.read_csv(table)

for idx,row in PSYDB.iterrows():
    inds = np.where(generalisation.subject_id==row.UID)[0]
    if len(inds)>0:
        score=generalisation.iloc[inds[0]]['prob_y']
        PSYDB = PSYDB.set_value(idx,'MRIQC_score',score)
        PSYDB = PSYDB.set_value(idx,'MRIQC_pass',score<0.5)

PSYDB.to_csv(os.environ.get("DATABASE"),index=False)

########################################
# TAKE SUBSET OF SUBJECTS FOR ANALYSIS #
########################################

# freeze
SUBSET = PSYDB[PSYDB.datafreeze==1]
print(len(SUBSET))
#subset complete
SUBSET = SUBSET[SUBSET.subject_status_complete==2]
print(len(SUBSET))
#subset MRI finished
SUBSET = SUBSET[SUBSET.is_this_subject_a_patient!=0]
print(len(SUBSET))
#subset MRI available
SUBSET = SUBSET[SUBSET.in_nidb==1]
print(len(SUBSET))
#subset MRI available
SUBSET = SUBSET[SUBSET.exclude!=1]
print(len(SUBSET))

##################################################
# CHECK WHICH SUBJECTS HAVE RESULTS FOR ANALYSES #
##################################################

# SUBSET = pd.read_csv(os.path.join(os.environ.get("TABLEDIR"),'REDCAP_clean.csv'))

bidsdir = os.environ.get("BIDSDIR")
mriqcdir = os.environ.get("MRIQCDIR")
prepdir = os.environ.get("PREPDIR")
cleandir = os.environ.get("CLEANDIR")
condir = os.environ.get("CONDIR")

checking = {"bids":[],'mriqc':[],'prep':[],'con':[]}
for cols in checking.keys():
    SUBSET[cols]=0

for cols in checking.keys():
    for idx,row in SUBSET.iterrows():
        if cols == 'bids':
            call = os.path.exists(os.path.join(bidsdir,"sub-%s"%row.UID))
        elif cols == 'mriqc':
            call = np.logical_not(np.isnan(row.MRIQC_score))
        elif cols == 'prep':
            call = os.path.exists(os.path.join(prepdir,"sub-%s"%row.UID))
        elif cols == 'con':
            call = os.path.exists(os.path.join(condir,"sub-%s"%row.UID))
        if call:
            SUBSET = SUBSET.set_value(idx,cols,1)

SUBSET = SUBSET.reset_index()

# SUBSET[SUBSET.bids==0]
# len([x for x in os.listdir(os.environ.get("PREDIR")) if x.startswith("sub-")])
# mriqc = pd.read_csv(os.path.join(os.environ.get("MRIQCDIR"),'out/T1w.csv'))

###########################
# GET TRAIN, TEST AND DEV #
###########################

#stratified
if not 'CVSET' in SUBSET.columns:
    SUBSET['CVSET'] = ""
    if np.sum(SUBSET.CVSET=="")/float(len(SUBSET))>0:
        SUBSET.CVSET=""
        for status in [888,999]:
            samplesize = len(SUBSET[SUBSET.is_this_subject_a_patient==status])
            sizes = {}
            sizes['train'] = int(0.6*samplesize)
            sizes['dev'] = int(0.2*samplesize)
            sizes['test'] = samplesize-sizes['train']-sizes['dev']
            for whichset in ['train','dev','test']:
                cond = np.logical_and(SUBSET.is_this_subject_a_patient==status, SUBSET.CVSET=="")
                inds = SUBSET[cond].index
                inds = np.random.choice(inds,size=sizes[whichset],replace=False)
                for ind in inds:
                    SUBSET = SUBSET.set_value(ind,'CVSET',whichset)

SUBSET.to_csv(os.environ.get("CLEANTABLE"),index=False)

###########################
# GET TRAIN, TEST AND DEV #
###########################

#SUBSET = SUBSET[SUBSET.CVSET!='test']
#SUBSET.to_csv(os.environ.get("TRAINTABLE"),index=False)
