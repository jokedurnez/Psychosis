import os
import pandas as pd
import shutil
import numpy as np

bidsdir = os.environ.get("BIDSDIR")
prepdir = os.environ.get("PREPDIR")
condir = os.environ.get("CONDIR")

participants = pd.read_csv(os.path.join(os.environ.get("TABLEDIR"),'REDCAP_clean.csv'))

remove = False

def remove_con(idx,subject):
    condir = os.environ.get("CONDIR")
    codedir = os.environ.get("CODEDIR")
    consub = os.path.join(condir,'sub-%s'%participant)
    if os.path.exists(consub):
        shutil.rmtree(consub)
        print("removed %s"%consub)
    for suffix in ['.err','.out']:
        logsub = os.path.join(codedir,'04_connectome/01_timeseries_cleaning/logs/CLEAN_%i%s'%(idx,suffix))
        if os.path.exists(logsub):
            os.remove(logsub)
            print("removed %s"%logsub)

rerun_clean = []

for idx,row in participants.iterrows():
    participant = row.UID
    bidssub = os.path.join(bidsdir,"sub-%s"%participant,'func')
    rsbids = [x[13:][:-7] for x in os.listdir(bidssub) if x.endswith('bold.nii.gz')]
    # check preprocessing
    prepsub = os.path.join(prepdir,'sub-%s'%participant,'MNINonLinear/Results')
    if not os.path.exists(prepsub):
        print("preprocessing folder does not exist: %s - index: %i"%(participant,idx))
        continue
    rsprep = os.listdir(prepsub)
    undone = set(rsbids)-set(rsprep)
    if len(list(undone))>0:
        print("incomplete preprocessing for subject: %s - index: %i"%(participant,idx))
        allundone.append(participant)
        idxundone.append(idx)
        prepsubdir = os.path.join(prepdir,'sub-%s'%participant)
        if remove:
            shutil.rmtree(prepsubdir)
        for suffix in ['.err','.out']:
            logfile = os.path.join(os.environ.get('CODEDIR'),'logs','PREP_%i%s'%(idx,suffix))
            if os.path.exists(logfile):
                if remove:
                    os.remove(logfile)
        logdir = os.path.join(os.environ.get('CODEDIR'),'logs',participant)
        if os.path.exists(logdir):
            if remove:
                shutil.rmtree(logdir)
    # check connectome
    consub = os.path.join(condir,'sub-%s'%participant)
    if not os.path.exists(consub):
        if remove:
            remove_con(idx,participant)
        print("cleaned folder does not exist: %s - index: %i - removed logs"%(participant,idx))
        rerun_clean.append(idx)
        continue
    consub = os.path.join(condir,'sub-%s'%participant)
    rscon = os.listdir(consub)
    rscon = [x for x in rscon if x.startswith('task-rest')]
    rsprep = [x for x in rsprep if x.startswith('task-rest')]
    undone = set(rsprep)-set(rscon)
    if len(list(undone))>0:
        if remove:
            remove_con(idx,participant)
        rerun_clean.append(idx)
        print("incomplete cleaning for subject: %s - index: %i - removed all"%(participant,idx))
