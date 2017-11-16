import os
import numpy as np
import pandas as pd
import sys

bidsdir = os.environ.get("BIDSDIR")
cleantable = pd.read_csv(os.environ.get("CLEANTABLE"))

for idx,row in cleantable.iterrows():
    if not row.exclude==1:
        funcs = os.listdir(os.path.join(bidsdir,"sub-%s"%row.UID,'func'))
        funcs = [x for x in funcs if x.endswith("bold.nii.gz") and 'rest' in x]
        if len(funcs)>4:
            print("%s: too many resting state sessions"%row.UID)
        anats = os.listdir(os.path.join(bidsdir,"sub-%s"%row.UID,'anat'))
        anats = [x for x in anats if x.endswith(".nii.gz")]
        if len(anats)>2:
            print("%s: too many resting anatomical sessions"%row.UID)
