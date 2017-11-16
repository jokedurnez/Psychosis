import scipy.stats as stats
import numpy as np
import pandas as pd

def evaluate_factors(factortable):
    out = {}
    # chi square of residual matrix
    pvals = [stats.chi2.pdf(x,y) for x,y in zip(factortable.chisq,factortable.dof)]
    out["LRT_H0"]=sum(np.array(pvals)<0.05)
    print("Based on the likelihood ration test, Model(N)-Model(0), the minimum number of factors is %i"%out["LRT_H0"])

    # likelihood ration
    difs = np.diff(factortable.chisq)
    difdofs = np.diff(factortable.dof)
    pvals = [stats.chi2.pdf(-x,-y) for x,y in zip(difs,difdofs)]
    out['LRT_Hn-1'] = sum(np.array(pvals)<0.05)
    print("Based on the likelihood ration test, Model(b)-Model(n-1), the minimum number of factors is %i"%(out['LRT_Hn-1']+1))

    # RMSEA
    out['RMSE'] = sum(factortable.RMSEA>0.05)
    print("Based on the RMSEA, the minimum number of factors is %i"%(out['RMSE']))


    #kaiser criterion: number of eigenvalues > 1
    out['kaiser'] = sum(factortable['eigen']>1)
    print("Based on the kaiser criterion, the minimum number of factors is %i"%(out['kaiser']))

    # BIC
    out['BIC'] = np.where(np.min(factortable.BIC) == factortable.BIC)[0][0]
    print("Based on the BIC, the minimum number of factors is %i"%(out['RMSE']))
    out['eBIC'] = np.where(np.min(factortable.eBIC) == factortable.eBIC)[0][0]
    print("Based on the empirical BIC, the minimum number of factors is %i"%(out['eBIC']))

    # complexity
    out['complexity'] = np.where(np.max(factortable.complex)==factortable.complex)[0][0]
    print("Based on the complexity, the minimum number of factors is %i"%(out['complexity']))

    # SRMR (standardised root mean square residual)
    out['SRMR'] = sum(factortable.SRMR<0.08)
    print("Based on the standardised root mean square residual, the minimum number of factors is %i"%(out['SRMR']))

    # parallel analysis: extract factors until eigen values of data < eigen vanlues of random data
    out['parallel'] = np.min(np.where(factortable.parallel_data<factortable.parallel_sim)[0])
    print("Based on parallel analysis, the minimum number of factors is %i"%(out['parallel']))

    # map: minimum average partial correlation
    out['MAP'] = np.where(np.min(factortable.map)==factortable.map)[0][0]
    print("Based on the minimum average partial correlation method, the minimum number of factors is %i"%(out['MAP']))

    return out
