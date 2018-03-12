'''
    File name: nodes.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 10/31/2017
    Python Version: 2.7
    Description: Script to compute connectome
    Project: Psychosis
'''

from __future__ import division

from nilearn.input_data import NiftiMasker, NiftiMapsMasker, NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
from sklearn.covariance import GraphLassoCV
from sklearn.decomposition import FastICA
from matplotlib import pyplot as plt
from scipy.signal import lfilter
from operator import itemgetter
from collections import Counter
from datetime import datetime
from itertools import groupby
from nilearn import datasets
import nilearn.signal
import nibabel as nib
import nilearn.image
import pandas as pd
import numpy as np
import argparse
import nilearn
import sys
import os

CODEDIR = os.environ['CODEDIR']
subject = os.environ.get('SUBJECT')
cleandir = os.path.join(os.environ.get('CONDIR'),"sub-%s"%subject)

keys = os.listdir(cleandir)
#keys = np.array([x.split("_bold") for x in keys if 'task' in x]).flatten()
keys = np.unique([x for x in keys if 'task' in x]).tolist()

print(datetime.now().strftime("%a %b %d %H:%M:%S"))
print("creating connectomes")

for gsr in ["_gsr",""]:
    for key in keys:
        print("extracting session "+key)
        # key = keys[0]
        imgfile = os.path.join(cleandir,key,key+'_removed_first10_despiked_masked_mvmreg%s_cmpc_bp.nii.gz'%gsr)

        ##################
        # 1 Gordon atlas #
        ##################

        atlasfile = os.path.join(os.environ.get("CODEDIR"),
                                 'postbids/rest/Parcels_MNI_111.nii')
        subcort_atlasfile = os.path.join(os.environ.get("CODEDIR"),
                                         'postbids/rest/HarvardOxford-sub-prob-1mm.nii.gz')
        cerebellum_atlasfile = os.path.join(os.environ.get("CODEDIR"),
                                            'postbids/rest/Cerebellum-MNIfnirt-prob-1mm.nii.gz')

        # extract signals
        masker = NiftiLabelsMasker(labels_img=atlasfile,standardize=True,detrend=False,low_pass=None,high_pass=None,verbose=5)
        subcortmasker = NiftiMapsMasker(maps_img=subcort_atlasfile,standardize=True,detrend=False,low_pass=None,high_pass=None,verbose=5)
        cerebellummasker = NiftiMapsMasker(maps_img=cerebellum_atlasfile,standardize=True,detrend=False,low_pass=None,high_pass=None,verbose=5)

        FDfile = os.path.join(cleandir,key,key+"_removed_first10_despiked_mvmreg.txt")
        FD = pd.read_csv(FDfile,"\t",header=None)
        FD = FD[[24,25]]
        FD.columns = ['dvars','FD']
        rmid = np.where(FD['FD'] > 0.5)[0]
        rmid = np.unique(np.concatenate((rmid,rmid+1,rmid-1)))
        short = np.append(False,np.logical_and(np.diff(rmid)>1,np.diff(rmid)<5))
        #gives Bool for indices when closer than 5 frames (but evidently more than 1)
        allrmid = [range(rmid[i-1],rmid[i])[1:] for i,val in enumerate(short) if val==True]
        allrmid = np.sort([item for sublist in allrmid for item in sublist]+rmid.tolist())
        ntp = nib.load(imgfile).shape[3]-len(allrmid)
        percrem = len(allrmid)/nib.load(imgfile).shape[3]

        rmidfile = os.path.join(cleandir,key,key+"_rmid.txt")
        np.savetxt(rmidfile,allrmid)
        percremfile = os.path.join(cleandir,key,key+"_percrem.txt")
        np.savetxt(percremfile,np.array([len(allrmid),ntp,percrem]))

        if percrem > 0.2:
            continue
            # if len(allrmid)>400:
            #     continue

        time_series = masker.fit_transform(imgfile)

        time_series_subcort = subcortmasker.fit_transform(imgfile)

        time_series_cerebellum = cerebellummasker.fit_transform(imgfile)

        time_series = np.concatenate((time_series,time_series_subcort,time_series_cerebellum),axis=1)

        time_series_scrubbed = np.delete(time_series,allrmid,axis=0)

        # Gordon_figure(correlation_matrix,limits=[-1,1])
        # plt.show()

        # save parcellated time series
        outfile = os.path.join(cleandir,key,key+"_Gordon_ts_scrubbed%s.csv"%gsr)
        np.savetxt(outfile,time_series_scrubbed)
        outfile = os.path.join(cleandir,key,key+"_Gordon_ts%s.csv"%gsr)
        np.savetxt(outfile,time_series)

        # static correlation
        outfile = os.path.join(cleandir,key,key+"_Gordon_correlation%s.csv"%gsr)
        correlation_measure = ConnectivityMeasure(kind='correlation')
        correlation_matrix = correlation_measure.fit_transform([time_series_scrubbed])[0]
        correlation_std = 1/np.sqrt(ntp-3)
        correlation_z = 1/2*np.log((1+correlation_matrix)/(1-correlation_matrix))#/correlation_std
        np.fill_diagonal(correlation_z,0)
        np.savetxt(outfile,correlation_z)

        # static correlation
        outfile = os.path.join(cleandir,key,key+"_Gordon_partial_correlation%s.csv"%gsr)
        correlation_measure = ConnectivityMeasure(kind='partial correlation')
        correlation_matrix = correlation_measure.fit_transform([time_series_scrubbed])[0]
        correlation_z = 1/2*np.log((1+correlation_matrix)/(1-correlation_matrix))#/correlation_std
        np.fill_diagonal(correlation_z,0)
        np.savetxt(outfile,correlation_z)

            ##########################
            # 2 cartography - Gordon #
            ##########################

            # windows = 15
            # numcon = time_series_scrubbed.shape[0]-windows
            #
            # time_series_dynamic = np.zeros([333,333,numcon])
            # for tps in range(numcon):
            #     time_series_cut = time_series_scrubbed[tps:(tps+windows)]
            #     correlation_measure = ConnectivityMeasure(kind='correlation')
            #     time_series_dynamic[:,:,tps] = correlation_measure.fit_transform([time_series_cut])[0]
            #
            # time_series_2d = time_series_dynamic.reshape((int(time_series_dynamic.shape[0]**2),time_series_dynamic.shape[2]))
            #
            # outfile = os.path.join(OUTDIR,key+"_dynamics.csv")
            # np.savetxt(outfile,time_series_2d)

            # plt.imshow(correlation_z,interpolation="nearest",cmap="hot")
            #
            # n_components = 5
            # ica = FastICA(n_components=n_components, random_state=42)
            # signal = ica.fit_transform(time_series_2d)
            # mixing = ica.mixing_
            # signal = signal.reshape((time_series_dynamic.shape[0],time_series_dynamic.shape[0],5))
            #

            ###############
            # 3 AAL atlas #
            ###############

            # atlas = datasets.fetch_atlas_msdl()
            # atlasfile = atlas['maps']
            # masker = NiftiMapsMasker(maps_img=atlasfile,standardize=True,detrend=False,low_pass=None,high_pass=None,verbose=5)
            # time_series = masker.fit_transform(imgfile)
            #
            # time_series = np.concatenate((time_series,time_series_subcort,time_series_cerebellum),axis=1)
            #
            # time_series_scrubbed = np.delete(time_series,allrmid,axis=0)
            #
            # # save parcellated time series
            # outfile = os.path.join(OUTDIR,key+"_Msdl_ts_scrubbed.csv")
            # np.savetxt(outfile,time_series_scrubbed)
            # outfile = os.path.join(OUTDIR,key+"_Msdl_ts.csv")
            # np.savetxt(outfile,time_series)
            #
            # # static correlation
            # outfile = os.path.join(OUTDIR,key+"_MSDL_correlation.csv")
            # correlation_measure = ConnectivityMeasure(kind='correlation')
            # correlation_matrix = correlation_measure.fit_transform([time_series])[0]
            # correlation_z = 1/2*np.log((1+correlation_matrix)/(1-correlation_matrix))#/correlation_std
            # np.fill_diagonal(correlation_z,0)
            # np.savetxt(outfile,correlation_z)
            # # static correlation
            # outfile = os.path.join(OUTDIR,key+"_MSDL_partial_correlation.csv")
            #
            # correlation_measure = ConnectivityMeasure(kind='partial correlation')
            # correlation_matrix = correlation_measure.fit_transform([time_series])[0]
            # correlation_z = 1/2*np.log((1+correlation_matrix)/(1-correlation_matrix))#/correlation_std
            # np.fill_diagonal(correlation_z,0)
            # np.savetxt(outfile,correlation_z)
