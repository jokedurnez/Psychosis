from datetime import datetime
import nibabel as nib
import pandas as pd
import numpy as np
import warnings
import argparse
import sys
import os

participants = pd.read_csv(os.environ.get("CLEANTABLE"))
BIDSDIR = os.environ.get("BIDSDIR")
CONDIR = os.environ.get("CONDIR")
CODEDIR = os.environ.get("CODEDIR")
GORDONLABELS=os.environ.get("GORDONLABELS")
CEREBELLUMLABELS=os.environ.get("CEREBELLUMLABELS")
SUBCORTLABELS=os.environ.get("SUBCORTLABELS")
ATLASLABELS=os.environ.get("ATLASLABELS")

results = {x:[] for x in ["key","patient",'subject',"MRIQC_pass",'MOTION_pass','confile','gsconfile','gsfile','percrem']}
results = pd.DataFrame(results)

for idx,row in participants.iterrows():
    subject = row.UID
    subbids = os.listdir(os.path.join(BIDSDIR,"sub-%s/func"%subject))
    keys = np.unique(["_".join(x.split("_")[2:4]) for x in subbids if (x.endswith("bold.nii.gz") and 'rest' in x)])
    fds = []
    for key in keys:
        rmidfile = os.path.join(CONDIR,"sub-%s"%row.UID,"task-rest_%s_bold"%key,"task-rest_%s_bold_percrem.txt"%key)
        if not os.path.exists(rmidfile):
            print("no rmid file found for id %i - subject %s - key %s"%(idx,row.UID,key))
            continue
        gsfile = os.path.join(CONDIR,"sub-%s"%row.UID,"task-rest_%s_bold"%key,"task-rest_%s_bold_removed_first10_despiked_masked_mvmreg_cmpc_globalsignal.txt"%key)
        percrem = np.loadtxt(rmidfile)[2]
        res = {
            "key":key,
            "patient":row.is_this_subject_a_patient,
            "subject":row.UID,
            "MRIQC_pass":row.MRIQC_pass,
            'gsfile':gsfile,
            'percrem':percrem
        }
        if percrem > 0.2:
            res['MOTION_pass']=0
        else:
            res['MOTION_pass']=1
        confile = os.path.join(CONDIR,"sub-%s"%row.UID,"task-rest_%s_bold"%key,"task-rest_%s_bold_Gordon_correlation.csv"%key)
        gsconfile = os.path.join(CONDIR,"sub-%s"%row.UID,"task-rest_%s_bold"%key,"task-rest_%s_bold_Gordon_correlation_gsr.csv"%key)
        res['confile']=confile
        res['gsconfile']=gsconfile
        results = results.append(res,ignore_index=True)

print("Collecting Gordon connectomes")
Gordoncor = np.zeros([382,382,len(results)])
Gordoncor_gsr = np.zeros([382,382,len(results)])
for idx,row in results.iterrows():
    if row.MOTION_pass==1:
        Gordoncor[:,:,idx] = np.loadtxt(row.confile)
        Gordoncor_gsr[:,:,idx] = np.loadtxt(row.gsconfile)

print("Grabbing GS")
GS = np.zeros([405,len(results)])
for idx,row in results.iterrows():
    gs = np.loadtxt(row.gsfile)
    GS[:len(gs),idx] = gs

derdir = os.path.join((CONDIR),'derivatives')
if not os.path.exists(derdir):
    os.mkdir(derdir)

results.to_csv(os.path.join(derdir,"connectome_results.csv"))
np.save(os.path.join(derdir,"connectomes.npy"),Gordoncor)
np.save(os.path.join(derdir,"connectomes_gsr.npy"),Gordoncor_gsr)
np.save(os.path.join(derdir,"gs.npy"),GS)

outdir = os.path.join(derdir,'voxelwise_comparisons')
if not os.path.exists(outdir):
    os.mkdir(outdir)

print("Collecting gsr-beta's")
betas = np.zeros([91,109,91,len(results)])
for idx,(sub,key) in enumerate(zip(results['subject'],results['key'])):
    betafile = os.path.join(os.environ.get('CONDIR'),'sub-'+sub,"task-rest_%s_bold"%key,"task-rest_%s_bold_removed_first10_despiked_masked_mvmreg_smooth_gsr_betas.nii.gz"%key)
    betamap = nib.load(betafile).get_data()
    betas[:,:,:,idx] = betamap[:,:,:,15]

new_image = nib.Nifti1Image(betas, affine=nib.load(betafile).affine,header=nib.load(betafile).header)
statstotfile = os.path.join(outdir,"gsr_betas.nii.gz")
nib.save(new_image,statstotfile)

print("Collecting fALFFs")
alff = np.zeros([91,109,91,len(results)])
for idx,(sub,key) in enumerate(zip(results['subject'],results['key'])):
    alffile = os.path.join(os.environ.get('CONDIR'),'sub-'+sub,"task-rest_%s_bold"%key,"task-rest_%s_bold_removed_first10_despiked_masked_mvmreg_smooth_fALFF.nii.gz"%key)
    alffmap = nib.load(alffile).get_data()
    alff[:,:,:,idx] = alffmap

new_image = nib.Nifti1Image(alff, affine=nib.load(alffile).affine,header=nib.load(alffile).header)
statstotfile = os.path.join(outdir,"fALFF.nii.gz")
nib.save(new_image,statstotfile)

print("Collecting variance")
varmaps = np.zeros([91,109,91,len(results)])
for idx,(sub,key) in enumerate(zip(results['subject'],results['key'])):
    varfile = os.path.join(os.environ.get('CONDIR'),'sub-'+sub,"task-rest_%s_bold"%key,"task-rest_%s_bold_removed_first10_despiked_masked_mvmreg_smooth_variance.nii.gz"%key)
    varmap = nib.load(varfile).get_data()
    varmaps[:,:,:,idx] = varmap

new_image = nib.Nifti1Image(varmaps, affine=nib.load(varfile).affine,header=nib.load(varfile).header)
statstotfile = os.path.join(outdir,"variance.nii.gz")
nib.save(new_image,statstotfile)

print("Collecting reho")
reho = np.zeros([91,109,91,len(results)])
for idx,(sub,key) in enumerate(zip(results['subject'],results['key'])):
    rehofile = os.path.join(os.environ.get('CONDIR'),'sub-'+sub,"task-rest_%s_bold"%key,"task-rest_%s_bold_removed_first10_despiked_masked_mvmreg_smooth_reho.nii.gz"%key)
    rehomap = nib.load(rehofile).get_data()
    reho[:,:,:,idx] = rehomap

new_image = nib.Nifti1Image(reho, affine=nib.load(rehofile).affine,header=nib.load(rehofile).header)
statstotfile = os.path.join(outdir,"reho.nii.gz")
nib.save(new_image,statstotfile)
