import copy
from dipy.io import read_bvals_bvecs
import os
import json
import numpy as np

##############
# top level ##
##############

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

outfile = os.path.join(os.environ.get("BIDSDIR"),'task-rest_acq-LR_bold.json')
with open(outfile,'w') as fl:
    json.dump(TaskRestAcqLrBold,fl)


# TaskRestAcqLrSbref = copy.deepcopy(alltask)
# TaskRestAcqLrSbref['TaskName']='rest_acq-LR'
# TaskRestAcqLrSbref['RepetitionTime']=5.76
# TaskRestAcqLrSbref['PhaseEncodingDirection']='i-'

TaskRestAcqRlBold = copy.deepcopy(alltask)
TaskRestAcqRlBold['TaskName']='rest_acq-RL'
TaskRestAcqRlBold['PhaseEncodingDirection']='i'

outfile = os.path.join(os.environ.get("BIDSDIR"),'task-rest_acq-RL_bold.json')
with open(outfile,'w') as fl:
    json.dump(TaskRestAcqRlBold,fl)


# TaskRestAcqRlSbref = copy.deepcopy(alltask)
# TaskRestAcqRlSbref['TaskName']='rest_acq-RL'
# TaskRestAcqRlSbref['RepetitionTime']=5.76
# TaskRestAcqRlSbref['PhaseEncodingDirection']='i'

TaskNBackBold = copy.deepcopy(alltask)
TaskNBackBold['TaskName'] = 'nback'
TaskNBackBold['PhaseEncodingDirection'] = 'i'

outfile = os.path.join(os.environ.get("BIDSDIR"),'task-nback_bold.json')
with open(outfile,'w') as fl:
    json.dump(TaskNBackBold,fl)


# TaskNBackSbref = copy.deepcopy(alltask)
# TaskNBackSbref['TaskName'] = 'nback'
# TaskNBackSbref['RepetitionTime'] = 5.76
# TaskNBackSbref['PhaseEncodingDirection'] = 'i'

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
    outfile = os.path.join(os.environ.get("BIDSDIR"),'acq-dir%sLR_dwi.json'%direct)
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
    outfile = os.path.join(os.environ.get("BIDSDIR"),'acq-dir%sLR_dwi.json'%direct)
    with open(outfile,'w') as fl:
        json.dump(DWI_LR,fl)

#add intendedfor !

allbval = {'dir90':[],'dir91':[]}
allbvec = {'dir90':[],'dir91':[]}

subs = [x for x in os.listdir(os.environ.get("BIDSDIR")) if x.startswith("sub-")]
for sub in subs:
    # DWI (resaving, isn't read right by validator)
    subdir = os.path.join(os.environ.get('BIDSDIR'),sub,'dwi')
    if os.path.exists(subdir):
        for direction in ['dir90','dir91']:
            scans = [x for x in os.listdir(subdir) if x.endswith("dwi.nii.gz") and direction in x]
            for scan in scans:
                base = scan.split(".")[0]
                fbval = os.path.join(subdir,"%s.bval"%base)
                fbvec = os.path.join(subdir,"%s.bvec"%base)
                bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
                np.savetxt(fbval,bvals.tolist(),delimiter=' ',newline=' ',fmt='%d')
                np.savetxt(fbvec,np.transpose(bvecs),delimiter=' ',fmt='%f')
                # if bvals.shape[0]!=int(direction[::-1][:2][::-1]):
                #     print("subject %s not conform"%sub)
                # allbval[direction].append(bvals)
                # allbvec[direction].append(bvecs.flatten())
    #FMAP
    subdir = os.path.join(os.environ.get("BIDSDIR"),sub,'fmap')
    if os.path.exists(subdir):
        scans = [x for x in os.listdir(subdir) if x.endswith("epi.nii.gz")]
        funcs = []; anats = []
        if os.path.exists(os.path.join(os.environ.get("BIDSDIR"), sub, 'func')):
            funcall = os.listdir(os.path.join(os.environ.get("BIDSDIR"), sub, 'func'))
            funcs = filter(
                lambda x: "nii.gz" in x and 'bold' in x, funcall)
            funcs = [os.path.join("func",x) for x in funcs]
        if os.path.exists(os.path.join(os.environ.get("BIDSDIR"), sub, 'anat')):
            anatall = os.listdir(os.path.join(os.environ.get("BIDSDIR"), sub, 'anat'))
            anats = filter(lambda x: "nii.gz" in x, anatall)
            anats = [os.path.join("anat",x) for x in anats]
        allintended = funcs + anats
        allintended = [os.path.join(os.environ.get("BIDSDIR"),sub,x) for x in allintended]
        for scan in scans:
            base = scan.split(".")[0]
            fmap_json = {"IntendedFor":allintended}
            outfile = os.path.join(os.environ.get("BIDSDIR"),sub,'fmap','%s.json'%base)
            with open(outfile,'w') as fl:
                json.dump(fmap_json,fl)


# add dataset description if it doesn't exist yet
dataset_description = {
    'Name':'Psychosis project',
    'BIDSVersion':"1.0.0-rc2"
}

outfile = os.path.join(os.environ.get("BIDSDIR"),'dataset_description.json')
with open(outfile,'w') as fl:
    json.dump(dataset_description,fl)
