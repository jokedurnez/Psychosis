import numpy as np
import os

logdir = os.path.join(os.environ.get("CODEDIR"),'postbids/bin/hpc/logs')

def check_prep(logdir):

preplogdir = os.path.join(logdir,'prep')
fls = os.listdir(preplogdir)
nms = list(set([x.split(".")[0].split("_")[1] for x in fls]))

ers = {"running":[],"binding":[],'other':[],'done':[]}
for nm in nms:
    logfile = os.path.join(preplogdir,'prep_%s.out'%nm)
    if not os.path.exists(logfile):
        print("File does not exist: %s"%logfile)
        continue
    with open(logfile,'r') as fl:
        content = fl.readlines()
    teststring = 'GenericfMRIVolumeProcessingPipeline.sh - Completed'
    if content == []: # probably still running
        ers['running'].append(nm)
    elif not teststring in content[::-1][2]:
        oakbind = '/oak/stanford/groups/russpold/data/Psychosis/0.0.3/ does not exist'
        if oakbind in content[::-1][2]:
            ers['binding'].append(nm)
        else:
            ers['other'].append(nm)
    else:
        ers['done'].append(nm)
