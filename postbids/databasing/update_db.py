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
import glob
import json
import csv
import sys
import os

sys.path.append(os.environ.get("CODEDIR"))
from prebids.databasing import psydb
from prebids.dicom import dicom

# functions to check if bids is complete
def check_rest_complete(protocols,UID):
    incomplete = False
    funcdir = os.path.join(os.environ.get("BIDSDIR"),"sub-%s"%UID,'func')
    for mod in [('bold','BIC_v2'),('sbref','BIC_v2_SBRef')]:
        dbrest = [x for x in protocols if 'REST' in x and x.endswith(mod[1])]
        if len(dbrest)==0:
            continue
        if not os.path.exists(funcdir):
            print("Missing func directory while expecting scans for subject %s"%UID)
            continue
        bidsrest = [x for x in os.listdir(funcdir) if x.endswith("%s.nii.gz"%mod[0]) and 'task-rest' in x]
        out = check_exclusions(UID,'rest',mod[0])
        if not len(bidsrest)==(len(dbrest)-len(out)):
                print("Missing rest (%s) in subject %s: expected %i rests, found %i in bids folder"%(mod[0],UID,len(dbrest),len(bidsrest)))
                incomplete = True
    return incomplete

def check_dwi_complete(protocols,UID):
    incomplete = False
    dwidir = os.path.join(os.environ.get("BIDSDIR"),"sub-%s"%UID,'dwi')
    for mod in ['dwi','sbref']:
        if mod == 'dwi':
            dbdwi = [x for x in protocols if 'DWI' in x and not x.endswith("SBRef")]
        else:
            dbdwi = [x for x in protocols if 'DWI' in x and x.endswith("SBRef")]
        if len(dbdwi)==0:
            continue
        if not os.path.exists(dwidir):
            print("Missing dwi directory while expecting scans for subject %s"%UID)
            continue
        bidsdwi = [x for x in os.listdir(dwidir) if x.endswith("%s.nii.gz"%mod)]
        out = check_exclusions(UID,'dwi',mod)
        if not len(bidsdwi)==(len(dbdwi)-len(out)):
                print("Missing dwi (%s) in subject %s: expected %i dwis, found %i in bids folder"%(mod,UID,len(dbdwi),len(bidsdwi)))
                incomplete = True
    return incomplete

def check_anat_complete(protocols,UID):
    incomplete = False
    anatdir = os.path.join(os.environ.get("BIDSDIR"),"sub-%s"%UID,'anat')
    for mod in [('T1w','T1w_MPR_BIC_v1'),('T2w','T2w_SPC_BIC_v1')]:
        dbanat = [x for x in protocols if x.endswith(mod[1])]
        if len(dbanat)==0:
            continue
        if not os.path.exists(anatdir):
            print("Missing anat directory while expecting scans for subject %s"%UID)
            continue
        bidsanat = [x for x in os.listdir(anatdir) if x.endswith("%s.nii.gz"%mod[0])]
        out = check_exclusions(UID,'anat',mod[0])
        if not len(bidsanat)==(len(dbanat)-len(out)):
                print("Missing aant (%s) in subject %s: expected %i anat, found %i in bids folder"%(mod[0],UID,len(dbanat),len(bidsanat)))
                incomplete = True
    return incomplete

def check_exclusions(UID,protocol,suffix):
    with open(os.environ.get("EXCLUSION"),'r') as fl:
        rules = json.load(fl)[0]
    removed = []
    for k,v in rules['remove'].iteritems():
        if UID in v:
            removed.append(k)
    return [x for x in removed if protocol in x and x.endswith(suffix)]

def check_bids_complete(PSYDB):
    DB = pd.read_csv(os.environ.get("NIDBTABLE"))
    DB = psydb.remove_old(DB)
    DB = psydb.remove_spaces(DB,protocols=True)
    DB = psydb.database_exclude(DB)
    redo = []
    nobids = []
    donotproceed = []
    for idx,row in PSYDB.iterrows():
        subbids = os.path.join(os.environ.get("BIDSDIR"),"sub-%s"%row.UID)
        if row.UID == 'S6765IZN':
            # this subject will throw errors, but is due to empty files
            continue
        if not os.path.exists(subbids):
            print("No bids directory for %s, rerun analysis %i"%(row.UID,idx))
            nobids.append(idx)
            donotproceed.append(idx)
        protocols = DB[row.UID==DB.UID].Protocol
        check1 = check_rest_complete(protocols,row.UID)
        check2 = check_dwi_complete(protocols,row.UID)
        check3 = check_anat_complete(protocols,row.UID)
        if check1 or check2 or check3:
            redo.append(row.UID)
            donotproceed.append(idx)
    print("---------------------------------------------")
    print("Consider redownloading and processing subjects: %s"%",".join(redo))
    print("Bidsification incomplete for subjects: %s"%",".join([str(x) for x in nobids]))
    print("---------------------------------------------")
    return donotproceed

# check which analyses are done (folders exist, so should be verified with logs)
def check_analyses(PSYDB):
    dicomdir = os.environ.get("DICOMDIR")
    bidsdir = os.environ.get("BIDSDIR")
    mriqcdir = os.environ.get("MRIQCDIR")
    prepdir = os.environ.get("PREPDIR")
    cleandir = os.environ.get("CLEANDIR")
    condir = os.environ.get("CONDIR")
    checking = {"dicom":[],"bids":[],'mriqc':[],'prep':[],'con':[]}
    for cols in checking.keys():
        PSYDB[cols]=0
    for cols in checking.keys():
        for idx,row in PSYDB.iterrows():
            if cols == 'bids':
                call = os.path.exists(os.path.join(bidsdir,"sub-%s"%row.UID))
            elif cols == 'mriqc':
                call = np.logical_not(np.isnan(row.MRIQC_score))
            elif cols == 'prep':
                call = os.path.exists(os.path.join(prepdir,"sub-%s"%row.UID))
            elif cols == 'con':
                call = os.path.exists(os.path.join(condir,"sub-%s"%row.UID))
            elif cols == 'dicom':
                call = os.path.exists(os.path.join(dicomdir,str(row.UID)))
            if call:
                PSYDB.at[idx,cols] = 1
    return PSYDB

def add_mriqc(PSYDB):
    table = os.environ.get("QCTABLE")
    generalisation = pd.read_csv(table)
    for idx,row in PSYDB.iterrows():
        inds = np.where(generalisation.subject_id==row.UID)[0]
        if len(inds)>0:
            score=generalisation.iloc[inds[0]]['prob_y']
            PSYDB.at[idx,'MRIQC_score'] = score
            PSYDB.at[idx,'MRIQC_pass'] = score<0.5
    return PSYDB

def make_slurm_ready(nums):
    iterator = np.sort(nums)
    newlist = []
    for idx,val in enumerate(iterator):
        if idx==0:
            newlist.append(str(val))
            continue
        elif idx == len(iterator)-1:
            add = ",%i"%val if newlist[::-1][0]!="-" else str(val)
            newlist.append(add)
            continue
        if iterator[idx-1]==val-1 and iterator[idx+1]==val+1:
            if newlist[::-1][0]=='-':
                continue
            else:
                newlist.append("-")
        else:
            if newlist[::-1][0] == '-':
                newlist.append("%i"%val)
            else:
                newlist.append(",%i"%val)
    return "".join(newlist)

def check_bids_modalities(subject):
    subdir = os.path.join(os.environ.get("BIDSDIR"),"sub-%s"%subject)
    out = {x:False for x in ['dwi','t1','t2','fmap','rest','nback']}
    files = glob.glob('%s/*/*'%subdir)
    files = ["/".join(x.split("/")[9:]) for x in files]
    startend = [('dwi','dwi','','dwi.nii.gz',4),
                ('t1','anat','','T1w.nii.gz',1),
                ('t2','anat','','T2w.nii.gz',1),
                ('rest','func','task-rest','bold.nii.gz',1),
                ('nback','func','task-nback','bold.nii.gz',1),
                ('fmap','fmap','','epi.nii.gz',1)]
    for check in startend:
        fls = [x for x in files if x.startswith(check[1]) and check[2] in x and x.endswith(check[3])]
        if len(fls) >= check[4]:
            out[check[0]] = True
    return out

def checks(check,mod):
    if mod == 'todo_qc':
        return check['t1'] or check['t2'] or check['rest'] or check['nback']
    if mod == 'todo_prep':
        return check['t1'] and check['t2'] and check['rest'] and check['fmap']
    if mod == 'todo_dwi':
        return check['t1'] and check['t2'] and check['dwi']
    if mod == 'todo_rest':
        return check['t1'] and check['t2'] and check['rest']

def check_analyses_todo(participants):
    if not os.path.exists(os.path.join(os.environ.get("MRIQCDIR"),'derivatives')):
        qc_done = []
    else:
        qc_done = os.listdir(os.path.join(os.environ.get("MRIQCDIR"),'derivatives'))
        qc_done = list(np.unique([x.split("_")[0] for x in qc_done]))
    prep_done = os.listdir(os.environ.get("PREPDIR"))
    con_done = os.listdir(os.environ.get("CONDIR"))
    participants['todo_qc'] = 0
    participants['todo_prep'] = 0
    participants['todo_dwi'] = 0
    participants['todo_rest'] = 0

    for idx,row in participants.iterrows():
        check = check_bids_modalities(row.UID)
        # check mriqc:
        if not 'sub-%s'%row.UID in qc_done and checks(check,'todo_qc'):
            participants.at[idx,'todo_qc'] = 1
        if not 'sub-%s'%row.UID in prep_done and checks(check,'todo_prep'):
            participants.at[idx,'todo_prep'] = 1
        if not 'sub-%s'%row.UID in con_done and checks(check,'todo_rest'):
            participants.at[idx,'todo_rest'] = 1
        if checks(check,'todo_dwi'):
            participants.at[idx,'todo_dwi'] = 1

    out = {
        'qc':list(np.where(participants['todo_qc']==1)[0]),
        'prep':list(np.where(participants['todo_prep']==1)[0]),
        'dwi':list(np.where(participants['todo_dwi']==1)[0]),
        'rest':list(np.where(participants['todo_rest']==1)[0])
        }

    qc_print = make_slurm_ready(out['qc'])
    print('Run MRIQC on the following indexes: %s'%qc_print)
    prep_print = make_slurm_ready(out['prep'])
    print('Run preprocessing on the following indexes: %s'%prep_print)
    dwi_print = make_slurm_ready(out['dwi'])
    print('Run dwi on the following indexes (note that there s not a good check at this point): %s'%dwi_print)
    con_print = make_slurm_ready(out['rest'])
    print("Run clean on the following indexes: %s"%con_print)

    return out
