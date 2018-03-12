#!/usr/bin/env python

'''
    File name: generate_json.py
    Author: Joke Durnez
    Date created: 02/08/2018
    Date last modified: 02/08/2018
    Python Version: 2.7
    Description: Functions to
    Project: Psychosis
'''
from dipy.io import read_bvals_bvecs
import numpy as np
import copy
import json
import os

json.encoder.FLOAT_REPR = lambda o: format(o, '.10f')

##############
# top level ##
##############

def dwi_bval_bvec(subject):
    # DWI (resaving, isn't read right by validator)
    subdir = os.path.join(os.environ.get('BIDSDIR'),subject,'dwi')
    if not os.path.exists(subdir):
        return False
    for direction in ['dir90','dir91']:
        scans = [x for x in os.listdir(subdir) if x.endswith("dwi.nii.gz") and direction in x]
        for scan in scans:
            base = scan.split(".")[0]
            fbval = os.path.join(subdir,"%s.bval"%base)
            fbvec = os.path.join(subdir,"%s.bvec"%base)
            bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
            np.savetxt(fbval,bvals.tolist(),delimiter=' ',newline=' ',fmt='%d')
            np.savetxt(fbvec,np.transpose(bvecs),delimiter=' ',fmt='%f')

def fmap_intendedfor(subject):
    subdir = os.path.join(os.environ.get("BIDSDIR"),subject,'fmap')
    if not os.path.exists(subdir):
        return False
    scans = [x for x in os.listdir(subdir) if x.endswith("epi.nii.gz")]
    funcs = []; anats = []
    if os.path.exists(os.path.join(os.environ.get("BIDSDIR"), subject, 'func')):
        funcall = os.listdir(os.path.join(os.environ.get("BIDSDIR"), subject, 'func'))
        funcs = filter(
            lambda x: "nii.gz" in x and 'bold' in x, funcall)
        funcs = [os.path.join("func",x) for x in funcs]
    if os.path.exists(os.path.join(os.environ.get("BIDSDIR"), subject, 'anat')):
        anatall = os.listdir(os.path.join(os.environ.get("BIDSDIR"), subject, 'anat'))
        anats = filter(lambda x: "nii.gz" in x, anatall)
        anats = [os.path.join("anat",x) for x in anats]
    allintended = funcs + anats
    for scan in scans:
        base = scan.split(".")[0]
        fmap_json = {"IntendedFor":allintended}
        outfile = os.path.join(os.environ.get("BIDSDIR"),subject,'fmap','%s.json'%base)
        with open(outfile,'w') as fl:
            json.dump(fmap_json,fl)

def generate_subject(subject):
    dwi_bval_bvec(subject)
    fmap_intendedfor(subject)

def alltasks():
    alltask = {
        "EchoTime": 0.036,
        "EffectiveEchoSpacing": 0.000700012460221792,
        "MultibandAccelerationFactor": 8,
        'TotalReadoutTime': 0.05950105911885232,
        "SliceTiming": [0.0,0.262,0.525,0.087,0.35,0.612,0.175,0.438,0.0,0.262,0.525,0.087,0.35,0.612,0.175,0.438,0.0,0.262,0.525,0.087,0.35,0.612,0.175,0.438,0.0,0.262,0.525,0.087,0.35,0.612,0.175,0.438,0.0,0.262,0.525,0.087,0.35,0.612,0.175,0.438,0.0,0.262,0.525,0.087,0.35,0.612,0.175,0.438,0.0,0.262,0.525,0.087,0.35,0.612,0.175,0.438,0.0,0.262,0.525,0.087,0.35,0.612,0.175,0.438],
        'SliceEncodingDirection': 'k',
        'RepetitionTime':0.72
    }

    TaskRestAcqLrBold = copy.deepcopy(alltask)
    TaskRestAcqLrBold['TaskName']='rest_acq-LR'
    TaskRestAcqLrBold['PhaseEncodingDirection']='i-'

    for suffix in ['bold','sbref']:
        outfile = os.path.join(os.environ.get("BIDSDIR"),'task-rest_acq-LR_%s.json'%suffix)
        with open(outfile,'w') as fl:
            json.dump(TaskRestAcqLrBold,fl)

    TaskRestAcqRlBold = copy.deepcopy(alltask)
    TaskRestAcqRlBold['TaskName']='rest_acq-RL'
    TaskRestAcqRlBold['PhaseEncodingDirection']='i'

    for suffix in ['bold','sbref']:
        outfile = os.path.join(os.environ.get("BIDSDIR"),'task-rest_acq-RL_%s.json'%suffix)
        with open(outfile,'w') as fl:
            json.dump(TaskRestAcqRlBold,fl)

    TaskNBackBold = copy.deepcopy(alltask)
    TaskNBackBold['TaskName'] = 'nback'
    TaskNBackBold['PhaseEncodingDirection'] = 'i'

    for suffix in ['bold','sbref']:
        outfile = os.path.join(os.environ.get("BIDSDIR"),'task-nback_%s.json'%suffix)
        with open(outfile,'w') as fl:
            json.dump(TaskNBackBold,fl)

def anat_t1():
    T1 = {
        "PhaseEncodingDirection":'j-',
        "SliceEncodingDirection":'k',
        'RepetitionTime': 2.4,
        'EchoTime': 0.00207,
        'EffectiveEchoSpacing' : 6500. * 10**(-9),
        'TotalReadoutTime' : 6500. * 10**(-9)
    }

    outfile = os.path.join(os.environ.get("BIDSDIR"),'T1w.json')
    with open(outfile,'w') as fl:
        json.dump(T1,fl)

def anat_t2():
    T2 = {
        "PhaseEncodingDirection":'j-',
        "SliceEncodingDirection":'k',
        'RepetitionTime':3.2,
        'EchoTime':0.565,
        'EffectiveEchoSpacing':2300. * 10**(-9),
        'TotalReadoutTime':2300. * 10**(-9)
    }

    outfile = os.path.join(os.environ.get("BIDSDIR"),'T2w.json')
    with open(outfile,'w') as fl:
        json.dump(T2,fl)

def fmap():
    FmapLR = {
        'EchoTime':0.067,
        'EffectiveEchoSpacing':0.000700012460221792,
        'PhaseEncodingDirection':'i-',
        'RepetitionTime':7.6,
        'SliceEncodingDirection':'k',
        'TotalReadoutTime':0.05950105911885232
    }

    outfile = os.path.join(os.environ.get("BIDSDIR"),'dir-1_epi.json')
    with open(outfile,'w') as fl:
        json.dump(FmapLR,fl)

    FmapRL = {
        'EchoTime':0.067,
        'EffectiveEchoSpacing':0.000700012460221792,
        'PhaseEncodingDirection':'i',
        'RepetitionTime':7.6,
        'SliceEncodingDirection':'k',
        'TotalReadoutTime':0.05950105911885232
    }

    outfile = os.path.join(os.environ.get("BIDSDIR"),'dir-2_epi.json')
    with open(outfile,'w') as fl:
        json.dump(FmapRL,fl)

def dwi():
    DWI_LR = {
        'EchoTime':0.067,
        'EffectiveEchoSpacing':0.000700012460221792,
        'PhaseEncodingDirection':'i-',
        'RepetitionTime':7.6,
        'SliceEncodingDirection':'k',
        'TotalReadoutTime':0.05950105911885232,
        'MultiBandAccelerationFactor':3
    }

    for direct in ['90','91']:
        for suffix in ['dwi']:
            outfile = os.path.join(os.environ.get("BIDSDIR"),'acq-dir%sLR_%s.json'%(direct,suffix))
            with open(outfile,'w') as fl:
                json.dump(DWI_LR,fl)

    DWI_RL = {
        'EchoTime':0.067,
        'EffectiveEchoSpacing':0.000700012460221792,
        'PhaseEncodingDirection':'i',
        'RepetitionTime':7.6,
        'SliceEncodingDirection':'k',
        'TotalReadoutTime':0.05950105911885232,
        'MultiBandAccelerationFactor':3

    }

    for direct in ['90','91']:
        for suffix in ['dwi']:
            outfile = os.path.join(os.environ.get("BIDSDIR"),'acq-dir%sRL_%s.json'%(direct,suffix))
            with open(outfile,'w') as fl:
                json.dump(DWI_RL,fl)

def description():
    # add dataset description if it doesn't exist yet
    dataset_description = {
    'Name':'Psychosis project',
    'BIDSVersion':"1.0.0-rc2"
    }

    outfile = os.path.join(os.environ.get("BIDSDIR"),'dataset_description.json')
    with open(outfile,'w') as fl:
        json.dump(dataset_description,fl)

def generate_toplevel():
    bidsdir = os.environ.get("BIDSDIR")
    if not os.path.exists(bidsdir):
        os.mkdir(bidsdir)

    alltasks()
    anat_t1()
    anat_t2()
    dwi()
    fmap()
    description()
