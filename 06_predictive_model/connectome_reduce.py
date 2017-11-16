from __future__ import division
from sklearn.decomposition import KernelPCA,IncrementalPCA,TruncatedSVD,MiniBatchSparsePCA
from sklearn.cluster import FeatureAgglomeration, MiniBatchKMeans, KMeans
from sklearn.decomposition import PCA,FastICA,FactorAnalysis,SparsePCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.decomposition import FactorAnalysis, PCA
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.mixture import BayesianGaussianMixture
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import learning_curve
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import ShuffleSplit
from sklearn.cluster import FeatureAgglomeration
from sklearn.feature_extraction import image
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_curve, auc
from utils.prog import log_progress as lp
from matplotlib.patches import Rectangle
from sklearn.svm import SVC, LinearSVC
import statsmodels.formula.api as smf
from numpy import transpose as T
from IPython.display import HTML
import matplotlib.pyplot as plt
from collections import Counter
import statsmodels.api as sm
from utils import neuropsych
import scipy.stats as stats
from scipy import interp
import matplotlib as mpl
import sklearn.cluster
import nibabel as nib
import seaborn as sns
import datetime as dt
import pandas as pd
import numpy as np
import palettable
import warnings
import scipy
import time
import json
import sys
import os

CONDIR = os.environ.get("CONDIR")
CODEDIR = os.environ.get("CODEDIR")

# read in data
gsr = '' if True else '_gsr'
connectomes = np.load(os.path.join(CONDIR,'derivatives/connectomes%s.npy'%gsr))
results = pd.read_csv(os.path.join(CONDIR,'derivatives/connectome_results.csv'),index_col=0)
factorsolution = pd.read_csv(os.path.join(os.environ.get("TABLEDIR"),"neuropsych_factor.csv"),index_col=0)

# check MRIQC
passubs = []
for idx,row in factorsolution.iterrows():
    ids = np.where(row.UID==results.subject)[0]
    qcs = np.where(np.logical_and(results.MRIQC_pass==1, results.MOTION_pass==1))[0]
    idqc = set(ids).intersection(qcs)
    if not len(idqc)==0:
        passubs.append(row.UID)

labelsfile = os.path.join(os.environ.get("CODEDIR"),"04_connectome/utils/Parcels.xlsx")
labeltable = pd.read_excel(labelsfile)
subprob = [[x+333,x+10+333] for x in range(10)]
subprob = [x for sublist in subprob for x in sublist]
cort = range(353,382)
order = np.argsort(labeltable.Community).tolist()+subprob+cort
labelnames = list(labeltable.Community[order][:333])+['subcort']*21+['cerebellum']*28
labels = np.unique(labelnames).tolist()
labelnames_unsorted = list(labeltable.Community)+['subcort']*21+['cerebellum']*28
ncon = len(labelnames)

# clean connectome and table
ConClean = np.zeros([ncon,ncon,len(passubs)])
FacClean = pd.DataFrame({k:[] for k in factorsolution.columns})

for idx,sub in enumerate(passubs):
    ids = np.where(sub==results.subject)[0]
    qcs = np.where(np.logical_and(results.MRIQC_pass==1, results.MOTION_pass==1))[0]
    idqc = set(ids).intersection(qcs)
    con = np.mean(connectomes[:,:,np.array(list(idqc))],axis=2)
    con = con[:,order]
    con = con[order,:]
    ConClean[:,:,idx] = con
    FacRow = factorsolution.iloc[np.where(sub==factorsolution.UID)[0]]
    FacClean = FacClean.append(FacRow)

FacClean = FacClean.reset_index()

upid = np.triu_indices(ncon)
X_full = np.transpose(ConClean[upid])
Y_full = np.array([1 if x=='patient' else 0 for x in FacClean.patient])

def reduce_cormat(cormat,ncomp,algorithm):
    ncon = cormat.shape[0]
    nclusters = np.min([ncomp,ncon**2])
    upid = np.triu_indices(ncon)
    connectivity=image.grid_to_graph(n_x=ncon,n_y=ncon,mask=mask)
    corflat = cormat[upid]
    algorithm.n_components = ncomp
    algorithm.n_clusters = ncomp
    conred = np.transpose(algorithm.fit_transform(np.transpose(corflat)))
    return conred

def compute_roc(X_init,Y_init,classifier,cv):
    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)
    i = 0
    for train, test in cv.split(X_init, Y_init):
        probas_ = classifier.fit(X_init[train], Y_init[train]).predict_proba(X_init[test])
        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(Y_init[test], probas_[:, 1])
        tprs.append(interp(mean_fpr, fpr, tpr))
        tprs[-1][0] = 0.0
        roc_auc = auc(fpr, tpr)
        aucs.append(roc_auc)
        i += 1
    return mean_fpr,tprs,aucs

# create dict of clustering algorithms
mask = np.zeros([ncon,ncon])
upid = np.triu_indices(ncon)
mask[upid]=1
connectivity=image.grid_to_graph(n_x=ncon,n_y=ncon,mask=mask)
ward = FeatureAgglomeration(connectivity=connectivity,linkage='ward')

clustering_algorithms = {
    "ward":ward,
    'kmeans':MiniBatchKMeans(),
    'pca':PCA(),
    'sigmoidPCA':KernelPCA(kernel='sigmoid'),
    'incrementalPCA':IncrementalPCA(),
    'fica':FastICA(),
    'SVD':TruncatedSVD(),
    'fa':FactorAnalysis(),
    'sparsepca':MiniBatchSparsePCA()
       }


prediction_algorithms = {
    "LDA": LinearDiscriminantAnalysis(),
    "QDA": QuadraticDiscriminantAnalysis(),
    "RandomForestClassifier": RandomForestClassifier(),
    "LogisticRegression": LogisticRegression(),
    #"RidgeClassifier":RidgeClassifier(),
    "NB":GaussianNB(),
    "KNN5":KNeighborsClassifier(n_neighbors=5),
    "SVM_lin":SVC(kernel='linear',probability=True),
    "SVM_poly":SVC(kernel='poly',probability=True),
    "SVM_rbf":SVC(kernel='rbf',probability=True),
    "NeuralNets10":MLPClassifier(hidden_layer_sizes=(10,)),
    "NeuralNets50":MLPClassifier(hidden_layer_sizes=(50,)),
    "NeuralNet100":MLPClassifier(hidden_layer_sizes=(100,))
    }

K = 5
cv = StratifiedKFold(n_splits=K,shuffle=True,random_state = 1096722206)


aucsdict = {}
learning_curves = {}

for k_cl,v_cl in clustering_algorithms.iteritems():
    for k_pr,v_pr in prediction_algorithms.iteritems():
        clus_auc_mn = []; clus_auc_sd = []
        for nclus in np.arange(20,30,5):
            ConRed = reduce_cormat(ConClean,nclus,v_cl)
            X_red = np.transpose(ConRed)
            X_red = X_red-np.mean(X_red,axis=0)/np.std(X_red,axis=0)
            X_red = np.nan_to_num(X_red)
            mean_fpr,tprs,aucs = compute_roc(X_red,Y_full,v_pr,cv)
            clus_auc_mn.append(np.mean(aucs))
            minsp = 0.1 if not v_pr == 'KNN20' else 0.2
        train_sizes, train_scores, test_scores = learning_curve(v_pr,
                                                                X_red, Y_full, cv=cv,
                                                                train_sizes=np.linspace(minsp,1.0,10))
        aucsdict["%s_%s"%(k_cl,k_pr)]=clus_auc_mn
        learning_curves["%s_%s"%(k_cl,k_pr)] = (train_sizes,train_scores,test_scores)

aucfile = os.path.join(os.environ.get("CONDIR"),'derivatives','aucs.json')
with open(aucfile,'w') as fp:
    json.dump(aucsdict,fp)

learningfile = os.path.join(os.environ.get("CONDIR"),'derivatives','learningcurves.json')
with open(learningfile,'w') as fp:
    json.dump(learning_curves,fp)
