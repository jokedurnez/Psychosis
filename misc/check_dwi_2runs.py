import os
import pandas as pd
import shutil
import numpy as np

bidsdir = os.environ.get("BIDSDIR")
prepdir = os.environ.get("PREPDIR")
condir = os.environ.get("CONDIR")

expected = set(['acq-dir90RL','acq-dir90LR','acq-dir91RL','acq-dir91LR'])

participants = pd.read_csv(os.path.join(os.environ.get("TABLEDIR"),'REDCAP_clean.csv'))
nodwi = []
doubles = []
missingpars = []

for idx,row in participants.iterrows():
    participant = row.UID
    dwisub = os.path.join(bidsdir,"sub-%s"%participant,'dwi')
    if not os.path.exists(dwisub):
        nodwi.append(participant)
    else:
        dwis = os.listdir(dwisub)
        dwis = [x for x in dwis if x.endswith('.nii.gz')]
        # check doubles
        doubles += [x for x in dwis if 'run-2' in x]
        pars = set([x.split("_")[1] for x in dwis])
        if not(len(expected-pars)==0):
            missingpars.append("sub-%s_%s"%(participant,str(expected-pars)))


for d in doubles:
    run1 = d.replace('run-2','run-1')
    sub = d.split("_")[0]
    file1 = os.path.join(bidsdir,sub,'dwi',run1)
    os.remove(file1)
