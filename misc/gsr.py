import os
import sys
import pandas as pd
import nibabel as nib
import numpy as np
import argparse
from datetime import datetime
from scipy.signal import periodogram,detrend


CONDIR = os.environ.get("CONDIR")
CONDIR = os.path.join(os.environ.get("BIDSDIR"),"derivatives","connectivity_Joke")

participants = pd.read_csv(os.environ.get("CLEANTABLE"))
participants['power'] = 0
participants['power'] = participants['power'].astype(object)
participants['sex'] = ''
participants['bmi'] = 0
participants['age'] = 0

DB = pd.read_csv(os.environ.get("NIDBTABLE"))
cols = list(DB.columns)
cols.insert(10,' new')
cols = [x[1:] for x in cols]
DB = DB.rename(columns={x:y for x,y in zip(list(DB.columns),cols)})
for idx,row in participants.iterrows():
    SUBJECT = row.db_uid
    DBrow = DB[DB.UID==' '+SUBJECT]
    participants = participants.set_value(idx,'sex',np.unique(DBrow['Sex'])[0][1:])
    participants = participants.set_value(idx,'bmi',np.unique(DBrow['bmi'])[0])
    participants = participants.set_value(idx,'age',np.unique(DBrow['AgeAtScan'])[0])

participants['bmi_cat']=0
participants.loc[participants.bmi>28,'bmi_cat']=1
participants['age_cat']=0
participants.loc[participants.bmi>38,'age_cat']=1

for idx,row in participants.iterrows():
    SUBJECT = row['db_uid']
    condir = os.path.join(CONDIR,"sub-%s"%SUBJECT)
    if not os.path.exists(condir):
        print("subject %s doesn't have a connectome analysis done"%SUBJECT)
        continue
    keys = os.listdir(condir)
    keys = [x for x in keys if x[:4]=='task']
    pows = np.zeros([len(keys),203])
    for ix,key in enumerate(keys):
        #key = keys[0]
        rmidfile = os.path.join(CONDIR,"sub-%s"%SUBJECT,key,"%s_rmid.csv"%key)
        rmid = np.loadtxt(rmidfile)
        # if len(rmid)/405.>0.2:
        #     continue
        gsfile = os.path.join(CONDIR,"sub-%s"%SUBJECT,key,"%s_removed_first10_masked_detrended_mvmreg_cmpc_GMglobal.txt"%key)
        if not os.path.exists(gsfile):
            print("key %s doesn't exist for subject %s, job no %i"%(key,SUBJECT,idx))
            continue
        gs = list(pd.read_csv(gsfile,sep='\t',header=None)[0])
        if len(gs)<405:
            print("too short")
            continue
        freq,pow=periodogram(gs,fs=1./0.72)
        pows[ix,:]=pow
    zerodx = np.where(np.mean(pows,axis=1)==0)[0]
    nonzerodx = np.array(list(set(range(len(keys)))-set(zerodx)))
    if len(nonzerodx)==0:
        continue
    else:
        pows = pows[nonzerodx,:]
        SUBPOW=np.mean(pows,axis=0)
        participants = participants.set_value(idx,'power',list(SUBPOW))

# generate two groups
#print("\n".join(participants.columns))
#print("\n".join(os.listdir(os.path.join(CONDIR,"sub-%s"%SUBJECT,key))))


conditioncol = 'do_you_currently_smoke'
vals = [1.0,2.0]
labs = ['Non-smoker','Smoker']

conditioncol = 'bmi_cat'
vals = [0,1]
labs = ['low bmi','high bmi']

conditioncol = 'age_cat'
vals = [0,1]
labs = ['young','old']

conditioncol = 'age_cat'
vals = [0,1]
labs = ['young','old']

conditioncol = 'is_this_subject_a_patient'
vals = [888,999]
labs = ['patient','control']

G1 = participants.power[np.logical_and(True,participants[conditioncol]==vals[0])].reset_index()
G1=G1.drop(np.where(G1.power==0)[0])
newG1 = np.zeros([len(G1),203])
k=0
for idx,row in G1.iterrows():
    if not row.power==0:
        newG1[k,:]=row['power']
        k+=1

G1mean = np.mean(newG1,axis=0)
G1CI = np.std(newG1,axis=0)/np.sqrt(newG1.shape[0])

G2 = participants.power[np.logical_and(True,participants[conditioncol]==vals[1])].reset_index()
G2=G2.drop(np.where(G2.power==0)[0])
newG2 = np.zeros([len(G2),203])
k=0
for idx,row in G2.iterrows():
    if not row.power==0:
        newG2[k,:]=row['power']
        k+=1

G = np.append(newG1,newG2,axis=0)
np.save("/home/jdurnez/pass.npy",G)

G2mean = np.mean(newG2,axis=0)
G2CI = np.std(newG2,axis=0)/np.sqrt(newG2.shape[0])

# make plot
import seaborn as sns
import matplotlib.pyplot as plt

cols = sns.color_palette("Paired")

figtitle = conditioncol
figfile = os.path.join(os.environ.get("FIGDIR"),"%s.jpg"%figtitle)
plt.plot(freq,G1mean,label=labs[0],color=cols[1])
plt.plot(freq,G2mean,label=labs[1],color=cols[3])
plt.plot(freq,G1mean+1.95*G1CI,color=cols[0])
plt.plot(freq,G1mean-1.95*G1CI,color=cols[0])
plt.plot(freq,G2mean+1.95*G2CI,color=cols[2])
plt.plot(freq,G2mean-1.95*G2CI,color=cols[2])
plt.xlim([0,0.1])
plt.legend()
plt.title(figtitle)
plt.savefig(figfile)

plt.show()

# make crosstable
pd.crosstab(participants.is_this_subject_a_patient,participants.bmi_cat).apply(lambda r: r/r.sum(), axis=1)
