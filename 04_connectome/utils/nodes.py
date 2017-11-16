from nipype.interfaces.base import BaseInterface, BaseInterfaceInputSpec, traits, File, TraitedSpec
from nipype.utils.filemanip import split_filename
import nibabel as nib
import pandas as pd
import numpy as np
import os

class LinearInterpolationInputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True,desc='volume to be interpolated',mandatory=True)
    movement_file = File(exists=True,desc='movement parameters outputted by TOPUP!!',mandatory=True)
    fd_threshold = traits.Float(desc='all volumes with FD higher than this value will be interpolated',mandatory=True)
    connect = traits.Int(desc='how many volumes should a series be to be considered?',mandatory=True)

class LinearInterpolationOutputSpec(TraitedSpec):
    out_file = File(exists=True,desc="interpolated volume")

class LinearInterpolation(BaseInterface):
    input_spec = LinearInterpolationInputSpec
    output_spec = LinearInterpolationOutputSpec

    def _run_interface(self,runtime):
        FD = ComputeFD(self.inputs.movement_file)
        rmID = IndexMissing(FD, self.inputs.fd_threshold,self.inputs.connect)

        data = nib.load(imgfile)
        imputed = Imputation(data.get_data(), rmID)

        new_img = nib.Nifti1Image(imputed,data.affine,data.header)
        nib.save(new_img,"interpolated.nii.gz")

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.volume
        _, base, _ = split_filename(fname)
        outputs['out_file'] = os.path.abspath(base + '_interpolated.nii')
        return outputs

def ComputeFD(movementfile):
        motion = pd.read_csv(movementfile,header=None)
        mpars = motion[range(6)].as_matrix()
        diff = mpars[:-1,:] - mpars[1:,:]
        diff[:,3:] *= np.pi*50*2/360.
        FD = np.abs(diff).sum(axis=1)
        FD = np.append([0],FD)
        return FD

def IndexMissing(FD, fd_threshold,connect):
    rmid = np.where(FD > fd_threshold)[0]
    short = np.append(False,np.logical_and(np.diff(rmid)>1,np.diff(rmid)<connect))
    #gives Bool for indices when closer than 5 frames (but evidently more than 1)
    allrmid = [range(rmid[i-1],rmid[i])[1:] for i,val in enumerate(short) if val==True]
    allrmid = np.sort([item for sublist in allrmid for item in sublist]+rmid.tolist())

    return allrmid

def Imputation(data,rmID):

    # separate indices in blocks
    ranges = []
    for k, g in groupby(enumerate(allrmid), lambda (i,x):i-x):
        group = map(itemgetter(1), g)
        ranges.append((group[0], group[-1]))

    # perform imputation for each block
    for block in ranges:
        if 0 in block:
            imputed = data[:,:,:,block[1]+1]
            numrep = block[1]
            data[:,:,:,:block[1]+1] = np.stack([imputed]*numrep,axis=3)
        elif (data.shape[3]-1) in block:
            imputed = data[:,:,:,block[0]-1]
            numrep = block[1]-block[0]+1
            data[:,:,:,block[0]:] = np.stack([imputed]*numrep,axis=3)
        else:
            blocklen = block[1]-block[0]+1
            increments = (data[:,:,:,block[1]+1]-data[:,:,:,block[0]-1])/(blocklen+1)
            for id,k in enumerate(range(block[0],block[1]+1)):
                imputed = data[:,:,:,block[0]-1]+(id+1)*increments
                data[:,:,:,k] = imputed

    return data
