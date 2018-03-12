'''
    File name: XX_combine_S1318RPT.py
    Author: Joke Durnez
    Date created: 02/13/2018
    Date last modified: 02/13/2018
    Python Version: 2.7
    Description: Script to put two sessions in 1 (because otherwise mismatch with rest of subs)
    Project: Psychosis
'''

import shutil
import os

bidsdir = os.environ.get("BIDSDIR")

subdir = os.path.join(bidsdir,'S1318RPT')
os.mkdir(subdir)

shutil.move(os.path.join(bidsdir,'S1318RPT1','func'),subdir)
shutil.move(os.path.join(bidsdir,'S1318RPT2','dwi'),subdir)
shutil.move(os.path.join(bidsdir,'S1318RPT2','anat'),subdir)

shutil.move(os.path.join(bidsdir,'S1318RPT1','fmap'),subdir)

for fls in os.listdir(os.path.join(bidsdir,'S1318RPT2','fmap')):
    oldfile = fls
    newfile = fls.replace("run-1",'run-3')
    oldpath = os.path.join(bidsdir,'S1318RPT2','fmap',oldfile)
    newpath = os.path.join(subdir,'fmap',newfile)
    print("renaming %s to %s"%(oldfile,newfile))
    os.rename(oldpath,newpath)

for root, dirs, files in os.walk(subdir):
    for fl in files:
        for ses in [1,2]:
            if 'S1318RPT%i'%ses in fl:
                oldpath = os.path.join(root,fl)
                newpath = oldpath.replace("S1318RPT%i"%ses,"S1318RPT")
                print("renaming %s to %s"%(oldpath,newpath))
                os.rename(oldpath,newpath)

shutil.rmtree(os.path.join(bidsdir,'S1318RPT1'))
shutil.rmtree(os.path.join(bidsdir,'S1318RPT2'))
