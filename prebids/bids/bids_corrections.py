#!/usr/bin/env python

'''
    File name: bids_corrections.py
    Author: Joke Durnez
    Date created: 02/08/2018
    Date last modified: 02/08/2018
    Python Version: 2.7
    Description: Functions to make changes after using heudiconv to bidsify
    Project: Psychosis
'''

import numpy as np
import shutil
import json
import os
import re

def change_foldername(ID,subdir,replace):
    BIDSDIR = os.environ.get("BIDSDIR")
    if replace or not os.path.exists(subdir):
        olddir = os.path.join(BIDSDIR, str(ID))
        if os.path.exists(subdir):
            set_permissions(subdir,'open')
            shutil.rmtree(subdir)
        os.rename(olddir,subdir)

def check_exclusions(ID,subdir):
    replaced = False

    with open(os.environ.get("EXCLUSION"),'r') as fl:
        rules = json.load(fl)

    exclusions = [x for x in rules if x['problem']=='repeats_handled'][0]['remove']

    for k,v in exclusions.iteritems():
        if ID in v:
            toremove = k.split("/")
            for ext in ['json','nii.gz','bval','bvec']:
                rmfile = os.path.join(subdir,toremove[0],"sub-%s_%s.%s"%(ID,toremove[1],ext))
                if os.path.exists(rmfile):
                    os.remove(rmfile)
                    replaced = True

    return replaced

def make_scans_consecutive(ID,subdir):
    make_anat_consecutive(ID,subdir)
    make_rest_consecutive(ID,subdir)
    make_dwi_consecutive(ID,subdir)

def make_dwi_consecutive(ID,subdir):
    dwidir = os.path.join(subdir,'dwi')
    if os.path.exists(dwidir):
        dwidir = os.listdir(dwidir)
        for acq in ["dir90LR",'dir90RL','dir91LR','dir91RL']:
            fls = [x for x in dwidir if acq in x]
            if len(fls) > 6:
                raise ValueError('The number of files for the DWI with direction %s for subject %s is incorrect'%(acq,ID))
            for fl in fls:
                oldfile = os.path.join(subdir,"dwi",fl)
                run = oldfile.split("_")[2]
                if not run=='run-1':
                    newfile = re.sub(run,'run-1',oldfile)
                    os.rename(oldfile,newfile)

def make_anat_consecutive(ID,subdir):
    anatdir = os.path.join(subdir,'anat')
    if os.path.exists(anatdir):
        anatdir = os.listdir(anatdir)
        for mod in ["T1w",'T2w']:
            for suffix in ['.nii.gz','.json']:
                fls = [x for x in anatdir if mod in x and x.endswith(suffix)]
                if len(fls)>1:
                    raise ValueError('There is more than 1 %s for subject %s'%(mod,ID))
                if len(fls)==0:
                    continue
                oldfile = os.path.join(subdir,"anat",fls[0])
                run = oldfile.split("_")[1]
                if not run=='run-1':
                    newfile = re.sub(run,'run-1',oldfile)
                    os.rename(oldfile,newfile)

def make_rest_consecutive(ID,subdir):
    restdir = os.path.join(subdir,'func')
    if os.path.exists(restdir):
        restdir = os.listdir(restdir)
    fls = [x for x in restdir if 'rest' in x]
    for acq in ['acq-LR','acq_RL']:
        acfls = [x for x in fls if acq in x]
        runs = np.unique([x.split("_")[3] for x in acfls]).tolist()
        nums = [int(x.split("-")[1]) for x in runs]
        if not len(nums)==0 and not len(nums)==max(nums):
            tochange = max(nums)-len(nums)
            for idx,run in enumerate(nums[::-1]):
                expected = 'run-%i'%(len(nums)-idx)
                true = 'run-%i'%run
                if not expected == true:
                    for ext in ["bold.nii.gz","sbref.nii.gz",'bold.json','sbref.json']:
                        oldfile = os.path.join(subdir,'func',"sub-%s_task-rest_%s_%s_%s"%(ID,acq,true,ext))
                        newfile = os.path.join(subdir,'func',"sub-%s_task-rest_%s_%s_%s"%(ID,acq,expected,ext))
                        os.rename(oldfile,newfile)

def set_permissions(path,direction):
    if direction=='open':
        for root, dirs, files in os.walk(path):
            # if '.heudiconv' in root:
            #     continue
            for momo in dirs:
                os.chmod(os.path.join(root, momo), 0770)
            for momo in files:
                os.chmod(os.path.join(root, momo), 0660)
    elif direction == 'close':
        for root, dirs, files in os.walk(path):
            for momo in dirs:
                os.chmod(os.path.join(root, momo), 0550)
            for momo in files:
                os.chmod(os.path.join(root, momo), 0440)

def concatenate_fmaps(ID,subdir):
    fmapdir = os.path.join(subdir,'fmap')
    if os.path.exists(fmapdir):
        contents = os.listdir(fmapdir)
        for direction in ['dir-1','dir-2']:
            fmap_out = "%s/sub-%s_%s_epi.nii.gz"%(fmapdir,ID,direction)
            fmap_dir = [os.path.join(fmapdir,x) for x in contents if direction in x and x.endswith('epi.nii.gz')]
            cmd = 'fslmerge -t %s %s'%(fmap_out," ".join(fmap_dir))
            os.popen(cmd)
            for fl in fmap_dir:
                os.remove(fl)
