import nibabel as nib
import pandas as pd
import numpy as np
import argparse
import sys
import os

idx = int(os.environ.get("SLURM_ARRAY_TASK_ID"))
suffix = ['gsr_betas','fALFF','variance','reho'][idx]

derdir = os.path.join(os.environ.get('CONDIR'),'derivatives/voxelwise_comparisons')
resultsfile = os.path.join(os.environ.get('CONDIR'),'derivatives/connectome_results.csv')
results = pd.read_csv(resultsfile)
results['patient_bin'] = [True if o==888 else False for o in results['patient']]

sigdir = os.path.join(os.path.join(derdir,suffix))
if not os.path.exists(sigdir):
    os.mkdir(sigdir)

#subset results and nifti
passidx = np.where(np.logical_and(results.MOTION_pass==1,results.MRIQC_pass==1))
results = results.iloc[passidx]
results = results.reset_index()

statstotfile = os.path.join(derdir,suffix+'.nii.gz')
statstot = nib.load(statstotfile).get_data()
statstot = statstot[:,:,:,passidx]

# create design matrix
des_c1 = np.zeros(len(results))
des_c1[np.where(results['patient_bin']==True)]=1
des_c2 = 1-des_c1

blocks = np.array([int(np.where(x==np.unique(results['subject']))[0][0])+1 for x in results['subject']])

destot = np.vstack((des_c1,des_c2)).transpose()
desfile = os.path.join(sigdir,suffix+"_design.csv")
np.savetxt(desfile,destot,delimiter='\t',newline='\n',fmt='%i')
contrast = np.array([[1,-1],[-1,1]]).transpose()
confile = os.path.join(sigdir,suffix+"_contrast.csv")
np.savetxt(confile,contrast,delimiter='\t',newline='\n',fmt='%i')
blocktot = blocks
blockfile = os.path.join(sigdir,suffix+"_blocks.csv")
np.savetxt(blockfile,blocktot,delimiter='\t',newline='\n',fmt='%i')

maskfile = os.path.join(derdir,"mask.nii.gz")

mask = np.zeros(statstot.shape)
mask[statstot!=0] = 1
mask = np.mean(mask,axis=3)
mask[mask<0.8]= 0
mask[mask>0]=1
new_image = nib.Nifti1Image(mask, affine=nib.load(statstotfile).affine,header=nib.load(statstotfile).header)
nib.save(new_image,maskfile)

np.load('stop')
# for nifti in [x for x in os.listdir(derdir) if x.endswith(".nii.gz")]:
#     niftifile = os.path.join(derdir,nifti)
#     ARR = nib.load(niftifile).get_data()
#     newimg = nib.Nifti1Image(ARR,header=new_image.header,affine=new_image.affine)
#     nib.save(newimg,niftifile)

palmcontainer = os.environ.get("PALMSINGULARITY")

outputprefix = os.path.join(sigdir,suffix+"_palm")
palmfile = os.path.join(os.environ.get("PSYDIR"),'05_connectome_group/01_compare_voxelwise/PALM/palm')
palmcmd = "singularity exec %s %s -i %s -m %s -d %s -eb %s -o %s -t %s -n 10000 -C 3.1 -Cstat 'mass' -noniiclass -ise" %(palmcontainer,palmfile,statstotfile,maskfile,desfile,blockfile,outputprefix,confile)

if 'FREESURFER_HOME' in os.environ:
    del os.environ['FREESURFER_HOME']

sys.exit(palmcmd)
