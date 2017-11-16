import os
import numpy as np
import pandas as pd
import seaborn as sns
from __future__ import division

HCPkeys = ["rfMRI_REST1_LR","rfMRI_REST1_RL","rfMRI_REST2_LR","rfMRI_REST2_RL"]
PSYkeys = ["task-rest_acq-LR_run-1_bold","task-rest_acq-RL_run-1_bold","task-rest_acq-LR_run-2_bold","task-rest_acq-RL_run-2_bold"]

HCPDIR = "/scratch/PI/russpold/data/HCP/"
PSYDIR = "/scratch/PI/russpold/data/psychosis/04_preprocessed"

diskdirs = [HCPDIR+d for d in os.listdir(HCPDIR)]
subdirs = []
for diskdir in diskdirs:
    sd = [os.path.join(diskdir,d) for d in os.listdir(diskdir)]
    subdirs += sd

avg = np.zeros([len(subdirs)*4,6])
k = 0
percentage = []
for subdir in subdirs:
    for key in HCPkeys:
        print(k)
        rundir = subdir+"/MNINonLinear/Results"+"/"+key
        if os.path.isdir(rundir):
            mpars = np.loadtxt(rundir+"/Movement_Regressors.txt")[:,:6]
            diff = mpars[:-1,:] - mpars[1:,:]
            avg[k,:] = np.mean(np.abs(diff),axis=0)
            diff[:,3:] *= np.pi*50*2/360.
            fd_res = np.abs(diff[:6]).sum(axis=1)
            fd_res = np.append([0],fd_res)
            percentage.append(np.sum(fd_res>0.5)/len(fd_res))
            k = k+1

avg_HCP = avg[:k,:]

labels = ["x_trans",'y_trans','z_trans','x_rot','y_rot','z_rot']
for x in [3,4,5,0,1,2]:
    plt.plot(diff[:,x],label=labels[x])

plt.legend()
plt.show()


subdirs = [PSYDIR+"/"+d for d in os.listdir(PSYDIR)]
avg = np.zeros([len(subdirs)*4,6])
k = 0
percentage = []
for subdir in subdirs:
    for key in PSYkeys:
        print(k)
        rundir = subdir+"/MNINonLinear/Results"+"/"+key
        if os.path.isdir(rundir):
            mpars = np.loadtxt(rundir+"/Movement_Regressors.txt")[:,:6]
            diff = mpars[:-1,:] - mpars[1:,:]
            avg[k,:] = np.mean(np.abs(diff),axis=0)[:6]
            diff[:,3:] *= np.pi*50*2/360.
            fd_res = np.abs(diff[:6]).sum(axis=1)
            fd_res = np.append([0],fd_res)
            percentage.append(np.sum(fd_res>0.5)/len(fd_res))
            k = k+1

avg_PSY = avg[:k,:]

HCP = pd.DataFrame(data = avg_HCP,columns = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z'])
HCP = pd.melt(HCP,value_vars = HCP.columns.tolist())
HCP['dataset'] = "HCP"

PSY = pd.DataFrame(data = avg_PSY,columns = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z'])
PSY = pd.melt(PSY,value_vars = PSY.columns.tolist())
PSY['dataset'] = 'PSY'

total = HCP.append(PSY)

lm = sns.boxplot(x='variable',y='value',hue="dataset",data=total)
axes = lm.axes
axes.set_ylim(0,0.15)
plt.show()

[os.listdir(y) for y in diskdirs]
[DISKDIR+]



[os.path.join(HCPDIR+d,os.listdir(HCPDIR+d)) for d in os.listdir(HCPDIR) if os.path.isdir(HCPDIR+d)]
