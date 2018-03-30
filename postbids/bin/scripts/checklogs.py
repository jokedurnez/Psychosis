import pandas as pd
import numpy as np
import shutil
import os
import sys

sys.path.append(os.path.join(os.environ.get('CODEDIR'),'postbids'))
from databasing import update_db

logdir = os.path.join(os.environ.get("CODEDIR"),'postbids/bin/hpc/logs')

def check_prep(logdir):
    preplogdir = os.path.join(logdir,'prep')
    fls = os.listdir(preplogdir)
    nms = list(set([x.split(".")[0].split("_")[1] for x in fls]))
    ers = {"empty":[],"binding":[],'other':[],'done':[]}
    for nm in nms:
        logfile = os.path.join(preplogdir,'prep_%s.out'%nm)
        if not os.path.exists(logfile):
            print("File does not exist: %s"%logfile)
            continue
        with open(logfile,'r') as fl:
            content = fl.readlines()
        teststring = 'GenericfMRIVolumeProcessingPipeline.sh - Completed'
        if content == []: # probably still running
            logfile = os.path.join(preplogdir,'prep_%s.err'%nm)
            if not os.path.exists(logfile):
                print("File does not exist: %s"%logfile)
                continue
            with open(logfile,'r') as fl:
                content = fl.readlines()
            if content == []:
                ers['empty'].append(nm)
            else:
                teststrings = ['error binding',"Image path doesn't exists"]
                test = [True if teststrings[0] in content[::-1][k] else False for k in range(len(content))]
                test += [True if teststrings[1] in content[::-1][k] else False for k in range(len(content))]
                if any(test):
                    ers['binding'].append(nm)
                else:
                    ers['other'].append(nm)
        else:
            test = [True if teststring in content[::-1][k] else False for k in range(10)]
            if any(test):
                ers['done'].append(nm)
            else:
                ers['other'].append(nm)
    return ers

def remove_prep(idxs,remove=False):
    participants = pd.read_csv(os.path.join(os.environ.get("CLEANTABLE")),sep='\t')
    for idx in list(idxs):
        for suffix in ['err','out']:
            logfile = os.path.join(logdir,'prep','prep_%s.%s'%(idx,suffix))
            if os.path.exists(logfile):
                if remove:
                    print("logfile removed: %s"%logfile)
                    os.remove(logfile)
            # get id
        subject = participants.UID[int(idx)]
        prepdir = os.path.join(os.environ.get("PREPDIR"),"sub-%s"%subject)
        if os.path.exists(prepdir):
            if remove:
                shutil.rmtree(prepdir)
                print("prepdir removed: %s"%prepdir)
        else:
            print("prepdir does not exist: %s"%prepdir)

def check_clean(logdir):
    cleanlogdir = os.path.join(logdir,'clean')
    fls = os.listdir(cleanlogdir)
    nms = list(set([x.split(".")[0].split("_")[1] for x in fls]))
    ers = {"empty":[],"binding":[],'other':[],'done':[]}
    for nm in nms:
        logfile = os.path.join(cleanlogdir,'clean_%s.out'%nm)
        if not os.path.exists(logfile):
            print("File does not exist: %s"%logfile)
            continue
        with open(logfile,'r') as fl:
            content = fl.readlines()
        teststring = 'Finished analyzing rest sessions'
        if content == []: # probably still running
            logfile = os.path.join(cleanlogdir,'clean_%s.err'%nm)
            if not os.path.exists(logfile):
                print("File does not exist: %s"%logfile)
                continue
            with open(logfile,'r') as fl:
                content = fl.readlines()
            if content == []:
                ers['empty'].append(nm)
            else:
                ers['other'].append(nm)
        else:
            test = [True if teststring in content[::-1][k] else False for k in range(min(len(content),10))]
            if any(test):
                ers['done'].append(nm)
            else:
                ers['other'].append(nm)
    return ers

def check_qc(logdir):
    qclogdir = os.path.join(logdir,'mriqc')
    fls = os.listdir(qclogdir)
    nms = list(set([x.split(".")[0].split("_")[1] for x in fls]))
    ers = {"empty":[],"binding":[],'other':[],'done':[]}
    for nm in nms:
        logfile = os.path.join(qclogdir,'mriqc_%s.out'%nm)
        if not os.path.exists(logfile):
            print("File does not exist: %s"%logfile)
            continue
        with open(logfile,'r') as fl:
            content = fl.readlines()
        teststring = 'Finished MRIQC for subject'
        if content == []: # probably still running
            logfile = os.path.join(qclogdir,'qc_%s.err'%nm)
            if not os.path.exists(logfile):
                print("File does not exist: %s"%logfile)
                continue
            with open(logfile,'r') as fl:
                content = fl.readlines()
            if content == []:
                ers['empty'].append(nm)
            else:
                ers['other'].append(nm)
        else:
            test = [True if teststring in content[::-1][k] else False for k in range(min(len(content),10))]
            if any(test):
                ers['done'].append(nm)
            else:
                ers['other'].append(nm)
    return ers

def check_dwi(logdir):
    dwilogdir = os.path.join(logdir,'dwi')
    fls = os.listdir(dwilogdir)
    nms = list(set([x.split(".")[0].split("_")[1] for x in fls]))
    ers = {"empty":[],"binding":[],'other':[],'done':[]}
    for nm in nms:
        logfile = os.path.join(dwilogdir,'DWI_%s.out'%nm)
        if not os.path.exists(logfile):
            print("File does not exist: %s"%logfile)
            continue
        with open(logfile,'r') as fl:
            content = fl.readlines()
        teststring = 'DiffPreprocPipeline.sh - Completed'
        if content == []: # probably still running
            logfile = os.path.join(dwilogdir,'DWI_%s.err'%nm)
            if not os.path.exists(logfile):
                print("File does not exist: %s"%logfile)
                continue
            with open(logfile,'r') as fl:
                content = fl.readlines()
            if content == []:
                ers['empty'].append(nm)
            else:
                ers['other'].append(nm)
        else:
            test = [True if teststring in content[::-1][k] else False for k in range(min(len(content),10))]
            if any(test):
                ers['done'].append(nm)
            else:
                ers['other'].append(nm)
    return ers

def remove_clean(idxs,remove=False):
    participants = pd.read_csv(os.path.join(os.environ.get("CLEANTABLE")),sep='\t')
    for idx in list(idxs):
        for suffix in ['err','out']:
            logfile = os.path.join(logdir,'clean','clean_%s.%s'%(idx,suffix))
            if os.path.exists(logfile):
                if remove:
                    print("logfile removed: %s"%logfile)
                    os.remove(logfile)
            # get id
        subject = participants.UID[int(idx)]
        cleandir = os.path.join(os.environ.get("CONDIR"),"sub-%s"%subject)
        if os.path.exists(cleandir):
            if remove:
                shutil.rmtree(cleandir)
                print("cleandir removed: %s"%cleandir)
        else:
            print("cleandir does not exist: %s"%cleandir)

# ers = check_prep(logdir)
# redo = ers['binding']+ers['other']
# redo = [int(x) for x in redo]
# #remove_prep(redo,remove=True)
# string = update_db.make_slurm_ready(redo)
# print("Redo preprocessing for: %s"%string)
#
# ers = check_qc(logdir)
# redo = ers['binding']+ers['other']
# redo = [int(x) for x in redo]
# #remove_prep(redo,remove=True)
# string = update_db.make_slurm_ready(redo)
# print("Redo mriqc for: %s"%string)
#
ers = check_dwi(logdir)
redo = ers['binding']+ers['other']
redo = [int(x) for x in redo]
#remove_clean(redo,remove=True)
string = update_db.make_slurm_ready(redo)
print("Redo dwi for %s"%string)

#61,146,148,156,158,160-168,176,178,179,185,186,188,322-353
