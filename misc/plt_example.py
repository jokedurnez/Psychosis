import os
import numpy as np
from nilearn.input_data import NiftiMasker, NiftiMapsMasker, NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
import pandas as pd
import copy
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

condir = os.environ.get('CONDIR')
subject = "S9905QEN"
cleandir = os.path.join(condir,"sub-"+subject)
outdir = os.environ.get("FIGDIR")
run = "task-rest_acq-LR_run-1_bold"
imgfile = os.path.join(os.environ.get('PREPDIR'),"sub-"+subject,'MNINonLinear/Results',run,run+".nii.gz")

filebase = os.path.join(cleandir,run,run+"_removed_first10")

FDfile = os.path.join(cleandir,run,run+"_mvmderiv.txt")
FD = pd.read_csv(FDfile,"\t",names=['dvar','FD'])['FD']
atlasfile = os.environ.get('CODEDIR')+"04_connectome/utils/Parcels_MNI_111.nii"
labelsfile = os.environ.get('CODEDIR')+"04_connectome/utils/Parcels.xlsx"

for gsr in ["_gsr",""]:
    masker = NiftiLabelsMasker(labels_img=atlasfile,standardize=True,detrend=True,low_pass=None,high_pass=None,verbose=5)
    time_series_or = masker.fit_transform(imgfile)
    time_series_ds = masker.fit_transform(os.path.join(filebase+"_despiked.nii.gz"))
    time_series_mv = masker.fit_transform(os.path.join(filebase+"_despiked_masked_mvmreg%s.nii.gz"%gsr))
    time_series_cc = masker.fit_transform(os.path.join(filebase+"_despiked_masked_mvmreg%s_cmpc.nii.gz"%gsr))
    time_series_bp = masker.fit_transform(os.path.join(filebase+"_despiked_masked_mvmreg%s_cmpc_bp.nii.gz"%gsr))

    mvreg = pd.read_csv(os.path.join(filebase+"_despiked_mvmreg.txt"),'\t')
    ccreg = pd.read_csv(os.path.join(filebase+"_despiked_masked_mvmreg%s_cmpc.txt"%gsr),'\t')

    new = copy.deepcopy(time_series_bp)
    rmid = np.where(FD > 0.5)[0]
    short = np.append(False,np.logical_and(np.diff(rmid)>1,np.diff(rmid)<5))
    #gives Bool for indices when closer than 5 frames (but evidently more than 1)
    allrmid = [range(rmid[i-1],rmid[i])[1:] for i,val in enumerate(short) if val==True]
    allrmid = np.sort([item for sublist in allrmid for item in sublist]+rmid.tolist())
    #allrmid = np.where(FD>0.5)
    new[allrmid,:] = np.max(new.T)

    # time_series_scrubbed = np.delete(time_series_bp,allrmid,axis=0)
    # correlation_measure = ConnectivityMeasure(kind='correlation')
    # correlation_matrix = correlation_measure.fit_transform([time_series_scrubbed])[0]
    # np.fill_diagonal(correlation_matrix,0)
    # plt.imshow(correlation_matrix)
    #
    # Gordon_figure(correlation_matrix,limits=[-1,1])
    #
    #
    f, ax = plt.subplots(8,sharex=True,figsize=(30,20))
    ax[0].imshow(time_series_or.T,aspect='auto',interpolation='nearest')
    ax[0].set_title("Original time series")
    ax[0].grid(False)
    ax[1].imshow(time_series_ds.T,aspect='auto',interpolation='nearest')
    ax[1].set_title("Time series after cutting off timepoints and despiking")
    ax[1].grid(False)
    # plot movement
    ax[2].plot(mvreg)
    ax[2].set_title("Movement regressors")
    ax[2].grid(False)
    ax[3].imshow(time_series_mv.T,aspect='auto',interpolation='nearest')
    ax[3].set_title("Time series after regressing out movement parameters")
    ax[3].grid(False)
    # plot cc
    ax[4].plot(ccreg)
    ax[4].set_title("CompCor regressors")
    ax[4].grid(False)
    ax[5].imshow(time_series_cc.T,aspect='auto',interpolation='nearest')
    ax[5].set_title("Time series after regressing out compcor parameters")
    ax[5].grid(False)
    ax[6].imshow(time_series_bp.T,aspect='auto',interpolation='nearest')
    ax[6].set_title("Time series after applying bandpass filter 0.01 < f < 0.125 Hz")
    ax[6].grid(False)
    ax[7].imshow(new.T,aspect='auto',interpolation='nearest')
    ax[7].set_title("Time series after removing high movement time points (framewise displacement > 0.5)")
    ax[7].grid(False)
    f.savefig(os.path.join(outdir,"preprocessing_example%s.pdf"%gsr),bbox_inches='tight')
