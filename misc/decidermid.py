from __future__ import division
import os
import pandas as pd
import numpy as np
import pickle
import warnings
import argparse
import nibabel as nib
import sys
import shutil
sys.path.append(os.path.join(os.environ.get("CODEDIR"),'04_connectome','01_timeseries_cleaning'))
from utils import nodes
outdir = os.environ.get("CONGROUPDIR")
prepdir = os.environ.get('PREPDIR')

# read in patients data
patients = pd.read_csv("/scratch/PI/russpold/data/psychosis/09_tables/REDCAP_clean.csv")
subjects = patients['scan_alt'].tolist()

# check BidsSLURM

subsincon = set([x[4:] for x in os.listdir(os.environ.get("CONDIR")) if x[0]=='s'])
subsindb = set(patients.scan_alt)
tobedeleted = list(subsincon - subsindb)

for subject in tobedeleted:
    #bidsdir = os.path.join(os.environ.get("BIDSDIR"),'sub-'+subject)
    #prepdir = os.path.join(os.environ.get("PREPDIR"),'sub-'+subject)
    condir = os.path.join(os.environ.get("CONDIR"),'sub-'+subject)
    #print(condir)
    shutil.rmtree(condir)

# make list of correlation files

noprep = []

LR1 = []
RL1 = []
LR2 = []
RL2 = []

for subject in np.sort(subjects):
    # if subject in ['S6463DJD','S3040SHP','S2451MWP','S8555KAD']:
    #     continue
    subprep = os.path.join(prepdir,"sub-"+subject,"MNINonLinear/Results")
    if not os.path.isdir(subprep):
        print("not preprocessed: %s"%subject)
        noprep.append(subject)
    else:
        funcprep = os.listdir(subprep)
        keys = [x for x in funcprep if 'rest' in x]

        for run in keys:

            longmovementfile = os.path.join(subprep,run,"Movement_Regressors.txt")
            movementfile = os.path.join(subprep,run,"Movement_Regressors_removed_first10.txt")
            movement = pd.read_csv(longmovementfile,delim_whitespace=True,header=None,engine='python')
            movement = movement.drop(range(10))
            movement = movement.reset_index()
            movement = movement.drop('index',1)
            movement.to_csv(movementfile,index=False,header=None)

            # compute FD
            FD = nodes.ComputeFD(movementfile)
            rmid = np.where(FD > 0.5)[0]
            rmid = np.unique(np.concatenate((rmid,rmid+1,rmid-1)))
            short = np.append(False,np.logical_and(np.diff(rmid)>1,np.diff(rmid)<5))
            #gives Bool for indices when closer than 5 frames (but evidently more than 1)
            allrmid = [range(rmid[i-1],rmid[i])[1:] for i,val in enumerate(short) if val==True]
            allrmid = np.sort([item for sublist in allrmid for item in sublist]+rmid.tolist())
            percrem = len(allrmid)/len(FD)

            if percrem > 0.2:
                if run == 'task-rest_acq-LR_run-1_bold':
                    LR1.append(subject)
                elif run == 'task-rest_acq-LR_run-2_bold':
                    LR2.append(subject)
                elif run == 'task-rest_acq-RL_run-1_bold':
                    RL1.append(subject)
                elif run == 'task-rest_acq-RL_run-2_bold':
                    RL2.append(subject)
                else:
                    print("subject %s - run %s discarded due to motion"%(subject,run))
