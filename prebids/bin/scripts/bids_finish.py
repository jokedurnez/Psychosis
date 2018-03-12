'''
    File name: bids_finish.py
    Author: Joke Durnez
    Date created: 02/13/2018
    Date last modified: 02/13/2018
    Python Version: 2.7
    Description: Script to make manual corrections to bids based on exclusions
    Project: Psychosis
'''
import os
import sys
import shutil

sys.path.append(os.environ.get("CODEDIR"))

from prebids.bids.bids_corrections import *
from prebids.bids.generate_json import *

subject = os.environ['SUBJECTLABEL']
bidsdir = os.environ['BIDSDIR']

# change foldername from SXXXXXXX to sub-SXXXXXXX
subdir = os.path.join(bidsdir,'sub-%s'%str(subject))
if os.path.exists(subdir):
    set_permissions(subdir,'open')
    shutil.rmtree(subdir)

change_foldername(subject,subdir,False)

# open permissions to changes
set_permissions(subdir,'open')

# check exclusions and rename scans
replaced = check_exclusions(subject,subdir)
#if replaced:
make_scans_consecutive(subject,subdir)

# concatenate fieldmaps
concatenate_fmaps(subject,subdir)

# generate jsons
subject = 'sub-%s'%subject
generate_subject(subject)

# close permissions to read only
set_permissions(subdir,'close')


# subs = [x[4:] for x in os.listdir(bidsdir) if x.startswith("sub-")]
# for subject in subs:
#     print("subject: %s"%subject)
#     subdir = os.path.join(bidsdir,'sub-%s'%str(subject))
#     set_permissions(subdir,'close')
#     fmapdir = os.path.join(subdir,'fmap')
#     if os.path.exists(fmapdir):
#         jsons = [x for x in os.listdir(fmapdir) if x.endswith("json") and 'run' in fl]
#         for fl in jsons:
#             os.remove(os.path.join(fmapdir,fl))
