from collections import Counter
import pandas as pd
import os
import shutil
from distutils.dir_util import copy_tree
import numpy as np
import json
import csv
from datetime import datetime
import pandas as pd
import tarfile
from utils import psydb

PSYDIR = os.environ.get("PSYDIR")
DICOMDIR = os.environ.get("DICOMDIR")
TABLEDIR = os.environ.get("TABLEDIR")
DB_file = os.environ.get("NIDBTABLE")
PSYDB_file = os.environ.get("CLEANTABLE")

def get_protocols(subdicoms):
    SH_protocols = os.listdir(subdicoms)
    SH_protocols = ["_".join(x.split("_")[1:]) if x[0].isdigit() else x for x in SH_protocols]
    SH_protocols = list(np.unique(SH_protocols))
    return SH_protocols

def check_protocols(DB,subject,protocols,altid):
    #cases where protocols start with numbers
    protocols = ["_".join(x.split("_")[1:]) if x.split("_")[0].isdigit() else x for x in protocols]
    DBprot = DB.Protocol[DB.UID==subject]
    DBprot = [x.replace(" ","_") for x in DBprot]
    DBtoo = ", ".join(list(set(DBprot)-set(protocols)))
    SHtoo = ", ".join(list(set(protocols)-set(DBprot)-set(['beh'])))
    if len(DBtoo)>0 or len(SHtoo)>0:
        print("There is not a perfect match between the database and sherlock for subject %s - %s, consider redo'ing these:"%(subject,altid))
        if len(DBtoo)>0:
            print("DB protocols too many: %s"%DBtoo)
        if len(SHtoo)>0:
            print("SH protocols too many: %s"%SHtoo)
    if set(DBprot).union(set(['beh']))==set(protocols):
        return True
    return False

def our_protocols():
    protocols = [
    # "localizer",
    "SpinEchoFieldMap_RL_BIC_v2",
    "SpinEchoFieldMap_LR_BIC_v2",
    #"BIAS_BC",
    #"BIAS_32ch",
    "rfMRI_REST_RL_BIC_v2_SBRef",
    "rfMRI_REST_RL_BIC_v2",
    "rfMRI_REST_LR_BIC_v2_SBRef",
    "rfMRI_REST_LR_BIC_v2",
    #"HPC_Nback_SBRef",
    #"HPC_Nback",
    "T1w_MPR_BIC_v1",
    "T2w_SPC_BIC_v1",
    #"DWI_dir90_RL_SBRef",
    #"DWI_dir90_RL",
    #"DWI_dir90_LR_SBRef",
    #"DWI_dir90_LR",
    #"DWI_dir91_RL_SBRef",
    #"DWI_dir91_RL",
    #"DWI_dir91_LR_SBRef",
    #"DWI_dir91_LR",
    ]
    return protocols

def check_complete(subject,SH_protocols):
    prot = our_protocols()
    intersect = list(set(prot) & set(SH_protocols))
    if len(intersect)==0:
        print("NOTE: Something's up with %s, there is no overlap with protocols we use."%(subject))
        return "No overlap"
    elif len(intersect)==len(prot):
        return True
    else:
        missing = [x for x in prot if not x in SH_protocols]
        return ",".join(missing)

# read in databases
PSYDB = pd.read_csv(PSYDB_file)
DB = pd.read_csv(DB_file)

DB = psydb.remove_old(DB)
DB = psydb.remove_spaces(DB,protocols=True)
DB = psydb.database_exclude(DB)
DB = DB.drop_duplicates()

with open(os.environ.get("EXCLUSIONTABLE"),'r') as fl:
    data = json.load(fl)

EXDB = pd.DataFrame(data)

DBshort = DB[['AltStudyID','UID']]
DBshort = DBshort.drop_duplicates()
# loop over subjects
for idx,row in DBshort.iterrows():
    altid = row.AltStudyID
    UID = row.UID
    subdicom = os.path.join(DICOMDIR,"%s"%UID)
    if not os.path.exists(subdicom):
        print("dicomdir not found for %s"%UID)
        continue
    sh_protocols = get_protocols(subdicom)
    same = check_protocols(DB,UID,sh_protocols,altid)
    complete = check_complete(UID,sh_protocols)
    if not type(complete)==str:
        exdbid = np.where(UID==EXDB.UID)[0]
        if len(exdbid)>0:
            if list(EXDB.action[exdbid])[0]=='incomplete':
                EXDB = EXDB.set_value(exdbid,'exclude',False)
                EXDB = EXDB.set_value(exdbid,'action','complete')
    if type(complete)==str:
        exdbid = np.where(UID==np.array(EXDB.UID))[0]
        if len(exdbid)>0:
            print("subject %s incomplete, missing %s, already in exclusionfile"%(UID,complete))
            EXDB.action[exdbid]='incomplete'
            EXDB.exclude[exdbid]=True
        else:
            print("subject %s incomplete, missing %s, adding to exclusionfile"%(UID,complete))
            # check to see if we can find subject_id
            PSYDBid = np.where(UID==PSYDB.UID)[0][0]
            newline = {
                "RC_id":PSYDB.subject_id[PSYDBid],
                "UID":UID,
                "action":"incomplete",
                "exclude":True,
                "note":PSYDB.if_there_are_repeated_scan[PSYDBid],
                "scan_id":altid
            }
            EXDB = EXDB.append(newline,ignore_index=True)

PSYDB.to_csv(PSYDB_file,index=False)
EXDB = EXDB.T.to_dict().values()
with open(os.environ.get("EXCLUSIONTABLE"),'w') as fl:
    json.dump(EXDB,fl)
