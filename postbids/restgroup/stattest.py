from __future__ import division
import statsmodels.formula.api as smf
import statsmodels.api as sm
import pandas as pd
import numpy as np
import scipy
import sys
import os
CONDIR = os.environ.get("CONDIR")

from rpy2 import robjects
from rpy2.robjects import r
import rpy2.robjects.packages as rpackages
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
rpackages.importr('lme4')


for qc in ['_noqc','']:
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
                r.assign("Rcon",robjects.FloatVector(connectomes[x,y,:]))
                r.assign("patient",robjects.StrVector(results['patient_bin']))
                r.assign("subject",robjects.StrVector(results['subject']))
                r('''
                    newdat <-  data.frame(c(patient),c(subject),c(Rcon))
                    colnames(newdat) <- c("patient","subject","conn")
                    model <- lmer(conn ~ patient + (1|subject),data=newdat)
                    tval <- coef(summary(model))[2,3]
                    pval <- 2*(1-pnorm(abs(tval)))
                           ''')
                t_Gordon[x] = r("tval")[0]
                p_Gordon[x] = r("pval")[0]

            outslicetGordon = os.path.join(statdir,"y_"+str(y).zfill(3)+"_t_Gordon%s.txt"%qc)
            outslicepGordon = os.path.join(statdir,"y_"+str(y).zfill(3)+"_p_Gordon%s.txt"%qc)
            np.savetxt(outslicetGordon,t_Gordon)
            np.savetxt(outslicepGordon,p_Gordon)
