'''
    File name: nodes.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 10/31/2017
    Python Version: 2.7
    Description: Script to clean timeseries
    Project: Psychosis
'''

from nilearn.input_data import NiftiMasker, NiftiMapsMasker, NiftiLabelsMasker
from nipype.utils.filemanip import split_filename
from scipy.signal import periodogram,detrend
from nipype.interfaces.fsl import Smooth
from nipype.interfaces import fsl, afni
import nipype.pipeline.engine as pe
from datetime import datetime
from nipype import algorithms
import pandas as pd
import nibabel as nib
import numpy as np
import argparse
import nilearn
import shutil
import sys
import os

sys.path.append(os.environ.get("CODEDIR"))

from postbids.rest.Text2Vest import Text2Vest
from postbids.rest import nodes, reho, utils

# get command line arguments

subject = os.environ.get("SUBJECT")

# if output already exist: overwrite?
redo = True

# load environment variables for psychosis PROJECT

cleandir = os.path.join(os.environ.get('CONDIR'),"sub-%s"%subject)
if os.path.exists(cleandir) and redo:
    shutil.rmtree(cleandir)
if not os.path.exists(cleandir):
    os.mkdir(cleandir)
prepdir = os.environ.get('PREPDIR')
CODEDIR = os.environ.get('CODEDIR')

print(datetime.now().strftime("%a %b %d %H:%M:%S"))
print("Start preparing masks for subject %s"%subject)

# get scan ID's

subprep = os.path.join(prepdir,"sub-"+subject,"MNINonLinear/Results")
keys = [x for x in os.listdir(subprep) if 'rest' in x]

os.chdir(cleandir)

########################
## CREATE WM/GM MASKS ##
########################

GMmaskfile = os.path.join(cleandir,"GM_mask.nii.gz")
WMmaskfile = os.path.join(cleandir,"WM_mask.nii.gz")
ribbonfile = os.path.join(prepdir,"sub-"+subject,"MNINonLinear",'ribbon.nii.gz')
reffile = os.path.join(prepdir,"sub-"+subject,"MNINonLinear",'T1w_restore.2.nii.gz')
utils.create_mask(GMmaskfile,WMmaskfile,ribbonfile,reffile)

#############################
## START CLEANING PIPELINE ##
#############################

for run in keys:

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("=============================================")
    print('Started analysing %s'%run)
    print("=============================================")

    rundir = os.path.join(cleandir,run)
    if not os.path.exists(rundir):
        os.mkdir(rundir)

    os.chdir(rundir)

    ############################
    # cut off first timepoints #
    ############################

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Cutting off first timepoints"%(subject,run))

    #in/out
    infile = os.path.join(subprep,run,run+".nii.gz") #original file
    outfile = os.path.join(rundir,run+"_removed_first10.nii.gz")

    #action
    totaltp = nib.load(infile).shape[3]
    if totaltp <= 10:
        continue
    fslroi = fsl.ExtractROI(in_file=infile,roi_file=outfile,t_min=10,t_size=totaltp-10)
    if not os.path.exists(outfile) or redo:
        fslroi.run()


    ###########
    # despike #
    ###########

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Despiking"%(subject,run))

    #in/out
    infile = outfile
    _,base,_=split_filename(infile)
    outfile = os.path.join(rundir,base+"_despiked.nii.gz")

    despiker = afni.Despike()
    despiker.inputs.in_file = infile
    despiker.inputs.args = '-NEW'
    despiker.inputs.out_file = outfile
    if not os.path.exists(outfile) or redo:
        despiker.run()

    ##############
    # APPLY MASK #
    ##############

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Masking"%(subject,run))

    infile = outfile
    _,base,_=split_filename(infile)
    outfile = os.path.join(rundir,base+"_masked.nii.gz")
    maskfile = os.path.join(subprep,run,"brainmask_fs.2.nii.gz")

    masker = fsl.maths.ApplyMask()
    masker.inputs.in_file = infile
    masker.inputs.mask_file = maskfile
    masker.inputs.out_file = outfile
    if not os.path.exists(outfile) or redo:
        masker.run()

    ####################################################
    # motion regression (and global signal regression) #
    ####################################################

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Regressing out motion"%(subject,run))

    movement_regressors = os.path.join(rundir,base+"_mvmreg.txt")
    movement_regressors_mat = os.path.join(rundir,base+"_mvmreg.mat")

    #++++++++++++++++++++
    # prepare regressors
    #++++++++++++++++++++

    # in/out (there's a lot of other files generated here)
    infile = outfile
    _,base,_=split_filename(infile)
    outfile_residuals = os.path.join(rundir,base+"_mvmreg.nii.gz")
    outfile_beta = os.path.join(rundir,base+"_mvmregbeta.nii.gz")
    motion_regressed = outfile_residuals

    # movement regressors
    longmovementfile = os.path.join(subprep,run,"Movement_Regressors.txt")
    movementfile = os.path.join(subprep,run,"Movement_Regressors_removed_first10.txt")
    movement = pd.read_csv(longmovementfile,delim_whitespace=True,header=None,engine='python')
    movement = movement.iloc[range(totaltp)]
    movementsq = movement**2
    movement = pd.concat([movement,movementsq],axis=1)
    movement = movement.drop(range(10))
    movement = movement.reset_index()
    movement = movement.drop('index',1)
    movement = movement.fillna(0)
    if not os.path.exists(movementfile) or redo:
        movement.to_csv(movementfile,index=False,header=None)

    # DVARS
    longdvarsfile = os.path.join(subprep,run,"Movement_RelativeRMS.txt")
    dvarsfile = os.path.join(subprep,run,"Movement_RelativeRMS_removed_first10.txt")
    motionDF = pd.read_csv(longdvarsfile,sep="",header=None,engine='python',names=['dvars'])
    motionDF = motionDF.drop(range(10))
    motionDF = motionDF.reset_index()
    motionDF = motionDF.drop('index',1)

    # compute FD
    FD = nodes.ComputeFD(movementfile)
    motionDF['FD'] = FD

    # save DVARS and FD
    motionfile = os.path.join(rundir,run+"_mvmderiv.txt")
    if not os.path.exists(motionfile) or redo:
        motionDF.to_csv(motionfile,sep="\t",header=None,index=False)

    # generate regressors
    movement = pd.read_csv(movementfile,sep=",",header=None,engine='python')
    #cte = pd.Series([1]*movement.shape[0]) # no longer necessary: data is centered
    reg = pd.concat([movement,motionDF],axis=1)
    if not os.path.exists(movement_regressors) or redo:
        reg.to_csv(movement_regressors,sep="\t",header=None,index=False)

    # generate regressors file readable for FSL
    create_reg = Text2Vest()
    create_reg.inputs.in_file = movement_regressors
    create_reg.inputs.out_file = movement_regressors_mat
    if not os.path.exists(movement_regressors_mat) or redo:
        create_reg.run()

    #++++++++++++++++++++++++++++
    # actual regression of motion
    #++++++++++++++++++++++++++++

    glm = fsl.GLM()
    glm.inputs.in_file = infile
    glm.inputs.design = movement_regressors_mat
    glm.inputs.dat_norm = False
    glm.inputs.var_norm = True
    glm.inputs.demean = True
    glm.inputs.out_res_name = outfile_residuals
    glm.inputs.out_file = outfile_beta
    if not os.path.exists(outfile_residuals) or redo:
        glm.run()

    #############################
    # global signal computation #
    #############################

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Computing global signal"%(subject,run))

    #in/out
    infile = outfile_residuals
    _,base,_=split_filename(infile)
    outfile_residuals_gs = os.path.join(rundir,base+"_gsr.nii.gz")
    outfile_beta_gs = os.path.join(rundir,base+"_gsrbeta.nii.gz")
    gs_regressors = os.path.join(rundir,base+"_gsr.txt")
    gs_regressors_mat = os.path.join(rundir,base+"_gsr.mat")

    #action
    data = nib.load(infile).get_data()
    meants = np.mean(data,axis=(0,1,2))
    meantsSeries = pd.Series(meants)
    meantsSeries_st = (meantsSeries-np.mean(meantsSeries))/np.std(meantsSeries)

    #############################
    # global signal regression #
    #############################

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Global signal regression"%(subject,run))

    meantsSeries_st.to_csv(gs_regressors,sep="\t",header=None,index=False)

    # generate regressors file readable for FSL
    create_reg = Text2Vest()
    create_reg.inputs.in_file = gs_regressors
    create_reg.inputs.out_file = gs_regressors_mat
    if not os.path.exists(gs_regressors_mat) or redo:
        create_reg.run()

    #+++++++++++++++++++++++++++++++++++++++++++++++++
    # actual regression of global signal
    #+++++++++++++++++++++++++++++++++++++++++++++++++

    glm = fsl.GLM()
    glm.inputs.in_file = infile
    glm.inputs.design = gs_regressors_mat
    glm.inputs.dat_norm = False
    glm.inputs.var_norm = True
    glm.inputs.demean = True
    glm.inputs.out_res_name = outfile_residuals_gs
    glm.inputs.out_file = outfile_beta_gs
    if not os.path.exists(outfile_beta_gs) or redo:
        glm.run()

    #######################################################
    #######################################################
    ## PATH 1: clean on both gsr-signal and nogsr-signal ##
    #######################################################
    #######################################################

    for infile in [outfile_residuals_gs,outfile_residuals]:

        ############
        # ANATICOR # --> not anaticor anymore, but high variance confounds (as in nilearn)
        ############

        print(datetime.now().strftime("%a %b %d %H:%M:%S"))
        print("%s in file %s: Regressing out high var cf"%(subject,run))

        #in/out
        _,base,_=split_filename(infile)
        regfile = os.path.join(rundir,base+"_cmpc.txt")
        regfile_mat = os.path.join(rundir,base+"_cmpc.mat")
        outfile_residuals = os.path.join(rundir,base+"_cmpc.nii.gz")
        outfile_beta = os.path.join(rundir,base+"_cmpcbeta.nii.gz")

        #compcor
        cv = nilearn.image.high_variance_confounds(infile,detrend=False)

        # prepare regressors
        cte = pd.Series([1]*cv.shape[0])
        reg = pd.concat([cte,pd.DataFrame(cv)],axis=1)
        reg.to_csv(regfile,sep="\t",header=None,index=False)

        create_reg = Text2Vest()
        create_reg.inputs.in_file = regfile
        create_reg.inputs.out_file = regfile_mat
        create_reg.run()

        #++++++++++++++++++++++++++++++++
        # actual regression of compcors
        #++++++++++++++++++++++++++++++++

        glm = fsl.GLM()
        glm.inputs.in_file = infile
        glm.inputs.design = regfile_mat
        glm.inputs.dat_norm = False
        glm.inputs.var_norm = False
        glm.inputs.demean = False
        glm.inputs.out_res_name = outfile_residuals
        glm.inputs.out_file = outfile_beta
        if not os.path.exists(outfile_beta) or redo:
            glm.run()

        ######################
        # bandpass filtering #
        ######################

        print(datetime.now().strftime("%a %b %d %H:%M:%S"))
        print("%s in file %s: Bandpass filtering"%(subject,run))

        infile = outfile_residuals
        _,base,_=split_filename(infile)
        outfile = os.path.join(rundir,base+"_bp.nii.gz")

        bandpass = afni.Bandpass()
        bandpass.inputs.in_file = infile
        bandpass.inputs.highpass = 0.01
        bandpass.inputs.lowpass = 0.125
        bandpass.inputs.normalize = False
        bandpass.inputs.outputtype = "NIFTI_GZ"
        bandpass.inputs.out_file = outfile
        if not os.path.exists(outfile) or redo:
            bandpass.run()

    ##########################################################
    ##########################################################
    ## PATH 2: smooth, compute global signal after cleaning ##
    ##########################################################
    ##########################################################

    _,base,_=split_filename(infile)
    outfile_gs = os.path.join(rundir,base+"_globalsignal.txt")

    # compute GS after all cleaning (in non-gsr situation)
    cleaned_no_filtering = nib.load(infile).get_data()
    meants = np.mean(cleaned_no_filtering,axis=(0,1,2))
    meantsSeries = pd.Series(meants)
    meantsSeries_st = (meantsSeries-np.mean(meantsSeries))/np.std(meantsSeries)
    np.savetxt(outfile_gs,meantsSeries_st)

    outfile_GMgs = os.path.join(rundir,base+"_GMglobalsignal.txt")
    masker = NiftiLabelsMasker(labels_img = GMmaskfile,standardize=False)
    ts = masker.fit_transform(infile)[:,0]
    np.savetxt(outfile_GMgs,ts)

    _,base,_=split_filename(outfile)
    outfile_gs = os.path.join(rundir,base+"_globalsignal.txt")

    # compute GS after all bpfilter (in non-gsr situation)
    cleaned_no_filtering = nib.load(outfile).get_data()
    meants = np.mean(cleaned_no_filtering,axis=(0,1,2))
    meantsSeries = pd.Series(meants)
    meantsSeries_st = (meantsSeries-np.mean(meantsSeries))/np.std(meantsSeries)
    np.savetxt(outfile_gs,meantsSeries_st)

    outfile_GMgs = os.path.join(rundir,base+"_GMglobalsignal.txt")
    masker = NiftiLabelsMasker(labels_img = GMmaskfile,standardize=False)
    ts = masker.fit_transform(outfile)[:,0]
    np.savetxt(outfile_GMgs,ts)

    #################################################################
    #################################################################
    ## PATH 3: smooth, compute ALFF, tempvar, regional homogeneity ##
    #################################################################
    #################################################################

    # skip this for now:
    continue

    ###############
    # Smooth data #
    ###############

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Smoothing data"%(subject,run))

    # input/output
    infile = motion_regressed
    _,base,_=split_filename(infile)
    outfile = os.path.join(rundir,base+"_smooth.nii.gz")

    bim = afni.BlurInMask()
    bim.inputs.mask = maskfile
    bim.inputs.in_file = infile
    bim.inputs.out_file = outfile
    bim.inputs.fwhm = 5.0
    bim.run()

    ##############################
    # GLM smoothed global signal #
    ##############################

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Computing global signal regressor"%(subject,run))

    # input/output
    infile = outfile
    _,base,_=split_filename(infile)
    betas = os.path.join(rundir,base+"_gsr_betas.nii.gz")

    glm = fsl.GLM()
    glm.inputs.in_file = infile
    glm.inputs.design = movement_regressors_mat
    glm.inputs.dat_norm = True
    glm.inputs.var_norm = True
    glm.inputs.demean = True
    glm.inputs.out_file = betas
    glm.run()

    ######################
    # Voxelwise variance #
    ######################

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Computing voxelwise variance"%(subject,run))

    #input/output
    infile = outfile
    _,base,_=split_filename(infile)
    outfile = os.path.join(rundir,base+"_variance.nii.gz")

    # compute variance (i.e. voxelwise distance from global signal)
    image = nib.load(infile)
    data = image.get_data()

    voxvar = np.std(data,axis=3)
    img = nib.Nifti1Image(voxvar,affine=image.get_affine(),header=image.get_header())
    img.to_filename(outfile)

    ######################
    # Compute ALFF/fALFF #
    ######################

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Computing fALFF"%(subject,run))

    # input/output
    infile = infile
    _,base,_=split_filename(infile)
    outfile = os.path.join(rundir,base+"_fALFF.nii.gz")

    # compute fALFF
    image = nib.load(infile)
    data = image.get_data()

    per = periodogram(data,axis=3,fs=0.72,nfft=720,scaling='spectrum')
    fALFFspectr = np.where(np.logical_and(per[0]>=0.01,per[0]<=0.08))
    amplitudes = np.sqrt(per[1])

    fALFFnum = np.sum(amplitudes[:,:,:,fALFFspectr[0]],axis=3)
    fALFFdenom = np.sum(amplitudes,axis=3)
    fALFF = fALFFnum/fALFFdenom
    fALFF = (fALFF-np.mean(fALFF))/np.std(fALFF)
    fALFF[np.where(np.isnan(fALFF))]=0
    fALFF_nii = nib.Nifti1Image(fALFF,affine=image.get_affine(),header=image.get_header())
    fALFF_nii.to_filename(outfile)

    # compute ALFF
    outfile = os.path.join(rundir,base+"_ALFF.nii.gz")

    ALFF = np.mean(amplitudes[:,:,:,fALFFspectr[0]],axis=3)
    ALFF = (ALFF-np.mean(ALFF))/np.std(ALFF)
    ALFF[np.where(np.isnan(ALFF))]=0
    ALFF_nii = nib.Nifti1Image(ALFF,affine=image.get_affine(),header=image.get_header())
    ALFF_nii.to_filename(outfile)

    ##########################
    # Regional Homogeneities #
    ##########################

    print(datetime.now().strftime("%a %b %d %H:%M:%S"))
    print("%s in file %s: Computing regional homogeneities"%(subject,run))

    # input/output
    infile = infile
    _,base,_=split_filename(infile)
    outfile = os.path.join(rundir,base+"_reho.nii.gz")

    # compute reho
    out = reho.compute_reho(infile, maskfile, 27,out_file=outfile)
