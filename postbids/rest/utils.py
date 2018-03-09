'''
    File name: utils.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 10/31/2017
    Python Version: 2.7
    Description: Create mask from ribbonfile
    Project: Psychosis
'''

import nibabel as nib
from nipype.interfaces import fsl
import numpy as np
import os

def create_mask(GMmaskfile,WMmaskfile,ribbonfile,reffile):

    ribbon = nib.load(ribbonfile)
    ribbondata = ribbon.get_data()
    ribbongrey = np.zeros(ribbondata.shape)
    ribbongrey[np.logical_or(ribbondata==3,ribbondata==42)]=1
    ribbonGREY = nib.Nifti1Image(ribbongrey,affine=ribbon.get_affine(),header=ribbon.get_header())
    ribbonGREY.to_filename(GMmaskfile)
    ribbonwhite = np.zeros(ribbondata.shape)
    ribbonwhite[np.logical_or(ribbondata==2,ribbondata==41)]=1
    ribbonWHITE = nib.Nifti1Image(ribbonwhite,affine=ribbon.get_affine(),header=ribbon.get_header())
    ribbonWHITE.to_filename(WMmaskfile)

    # downsample to 2mm MNI

    GMdownsample = fsl.FLIRT()
    GMdownsample.inputs.in_file = GMmaskfile
    GMdownsample.inputs.reference = reffile
    GMdownsample.run()

    WMdownsample = fsl.FLIRT()
    WMdownsample.inputs.in_file = WMmaskfile
    WMdownsample.inputs.reference = reffile
    WMdownsample.run()

    WMsmooth = fsl.maths.IsotropicSmooth()
    WMsmooth.inputs.in_file = WMdownsample._list_outputs()['out_file']
    WMsmooth.inputs.in_file = maskfile = WMdownsample._list_outputs()['out_file']
    WMsmooth.inputs.fwhm = 10
    WMsmooth.run()

    # load generated masks

    GM = nib.load(GMdownsample._list_outputs()['out_file'])
    WM = nib.load(WMsmooth._list_outputs()['out_file'])
    GMmask = GM.get_data()
    WMmask = WM.get_data()

    # binarise

    GMmore = np.where(np.logical_and(GMmask>WMmask,GMmask>0))
    WMmore = np.where(np.logical_and(WMmask>GMmask,WMmask>0.99))
    GMmask = np.zeros(GMmask.shape)
    GMmask[GMmore] = 1
    WMmask = np.zeros(WMmask.shape)
    WMmask[WMmore] = 1

    # write to files

    maskGREY = nib.Nifti1Image(GMmask,affine=GM.get_affine(),header=GM.get_header())
    maskGREY.to_filename(GMmaskfile)
    maskWHITE = nib.Nifti1Image(WMmask,affine=WM.get_affine(),header=WM.get_header())
    maskWHITE.to_filename(WMmaskfile)
