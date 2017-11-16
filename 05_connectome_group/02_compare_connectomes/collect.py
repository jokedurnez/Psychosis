import os
import sys
import numpy as np

CONDIR = os.environ.get("CONDIR")

print("collecting statistical tests")
statdir = os.path.join(CONDIR,"derivatives/t_stat_mixed_model")

statT = np.zeros([382,382])
statP = np.zeros([382,382])
statT_gsr = np.zeros([382,382])
statP_gsr = np.zeros([382,382])
mis = []
for qc in ['_noqc','']:
    for y in range(382):
        outslicetGordon_gsr = os.path.join(statdir+"_gsr","y_"+str(y).zfill(3)+"_t_Gordon%s.txt"%qc)
        outslicepGordon_gsr = os.path.join(statdir+"_gsr","y_"+str(y).zfill(3)+"_p_Gordon%s.txt"%qc)
        outslicetGordon = os.path.join(statdir,"y_"+str(y).zfill(3)+"_t_Gordon%s.txt"%qc)
        outslicepGordon = os.path.join(statdir,"y_"+str(y).zfill(3)+"_p_Gordon%s.txt"%qc)
        if not os.path.exists(outslicepGordon):
            print("not found %s"%outslicepGordon)
            mis.append(y)
            continue
        statT[:,y]=np.loadtxt(outslicetGordon)
        statP[:,y]=np.loadtxt(outslicepGordon)
        statT_gsr[:,y]=np.loadtxt(outslicetGordon_gsr)
        statP_gsr[:,y]=np.loadtxt(outslicepGordon_gsr)

    np.save(os.path.join(CONDIR,"derivatives/statT_mixed%s.npy"%qc),statT)
    np.save(os.path.join(CONDIR,"derivatives/statP_mixed%s.npy"%qc),statP)
    np.save(os.path.join(CONDIR,"derivatives/statT_mixed_gsr%s.npy"%qc),statT_gsr)
    np.save(os.path.join(CONDIR,"derivatives/statP_mixed_gsr%s.npy"%qc),statP_gsr)
