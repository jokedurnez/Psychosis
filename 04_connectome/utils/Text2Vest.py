from nipype.interfaces.base import BaseInterface, BaseInterfaceInputSpec, traits, File, TraitedSpec, isdefined
from nipype.interfaces.fsl.base import FSLCommand, FSLCommandInputSpec, Info
from nipype.utils.filemanip import split_filename
from operator import itemgetter
from itertools import groupby
import nibabel as nib
import numpy as np
import os

class Text2VestInputSpec(FSLCommandInputSpec):
    in_file = File(exists=True,desc='text-file with regressors',mandatory=True,argstr="%s",position=0)
    out_file = File(desc='destination mat-file',mandatory=True,argstr='%s',position=1)

class Text2VestOutputSpec(TraitedSpec):
    out_file = File(exists=False,desc="mat-file with regressors")

class Text2Vest(FSLCommand):
    input_spec = Text2VestInputSpec
    output_spec = Text2VestOutputSpec
    _cmd = "Text2Vest"

    def _list_outputs(self):
        outputs = self._outputs().get()
        return outputs
