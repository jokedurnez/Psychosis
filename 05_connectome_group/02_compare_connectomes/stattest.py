from __future__ import division
import statsmodels.formula.api as smf
import statsmodels.api as sm
import pandas as pd
import numpy as np
import scipy
import sys
import os
CONDIR = os.environ.get("CONDIR")

qc = '_noqc' if True else ''

for gsr in ["_gsr",""]:
    # read datasets
    Gordoncor = np.load(os.path.join(CONDIR,'derivatives/connectomes%s.npy'%gsr))
    results = pd.read_csv(os.path.join(CONDIR,'derivatives/connectome_results.csv'))
    results['patient_bin'] = ['True' if x==888 else 'False' for x in results['patient']]

    # subset only subjects with pass on QA
    if qc == '':
        QAid = np.where(results.MOTION_pass==1)[0]
    else:
        QAid = np.where(np.logical_and(results.MRIQC_pass==1,results.MOTION_pass==1))[0]

    results = results.iloc[QAid]
    results = results.reset_index()
    connectomes = Gordoncor[:,:,QAid]

    statdir = os.path.join(CONDIR,"derivatives/t_stat_mixed_model%s"%gsr)
    if not os.path.exists(statdir):
        os.mkdir(os.path.join(statdir))

    y = int(os.environ.get("SLURM_ARRAY_TASK_ID"))
    t_Gordon = np.zeros([382])
    p_Gordon = np.zeros([382])
    for x in range(382):
        print(x)
        if x == y:
            continue
        else:
            data = pd.DataFrame({"val":connectomes[x,y,:],"patient":results['patient_bin'],"subject":results['subject']})
            fit = smf.mixedlm('val ~ patient',data=data,groups=data.subject).fit()
            t_Gordon[x] = fit.tvalues['patient[T.True]']
            p_Gordon[x] = fit.pvalues['patient[T.True]']

    outslicetGordon = os.path.join(statdir,"y_"+str(y).zfill(3)+"_t_Gordon%s.txt"%qc)
    outslicepGordon = os.path.join(statdir,"y_"+str(y).zfill(3)+"_p_Gordon%s.txt"%qc)
    np.savetxt(outslicetGordon,t_Gordon)
    np.savetxt(outslicepGordon,p_Gordon)
