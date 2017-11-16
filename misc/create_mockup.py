import os
import shutil

BIDSDIR='/scratch/PI/russpold/data/AA_project/03_bids/'
MOCKDIR='/scratch/PI/russpold/data/AA_project/99_bids_mockup/'

subdirs = os.listdir(BIDSDIR)

for subdir in subdirs:
    os.mkdir(os.path.join(MOCKDIR,subdir))
    protdirs = os.listdir(os.path.join(BIDSDIR,subdir))
    for protdir in protdirs:
        os.mkdir(os.path.join(MOCKDIR,subdir,protdir))
        files = os.listdir(os.path.join(BIDSDIR,subdir,protdir))
        for file in files:
            if 'nii.gz' in file:
                os.mknod(os.path.join(MOCKDIR,subdir,protdir,file))
            else:
                src = os.path.join(BIDSDIR,subdir,protdir,file)
                dst = os.path.join(MOCKDIR,subdir,protdir,file)
                shutil.copyfile(src,dst)
