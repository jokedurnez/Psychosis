import os
import sys
import pandas as pd
import nibabel as nib
import numpy as np
import argparse
from datetime import datetime
from scipy.signal import periodogram,detrend
from xml.dom import minidom

GORDONLABELS=os.environ.get("GORDONLABELS")
CODEDIR = os.environ.get("CODEDIR")
CEREBELLUMLABELS=os.environ.get("CEREBELLUMLABELS")
SUBCORTLABELS=os.environ.get("SUBCORTLABELS")
ATLASLABELS=os.environ.get("ATLASLABELS")


labels = os.path.join(CODEDIR,"04_connectome/02_functional_connectivity/labels.csv")
labels = pd.read_csv(labels)
labels = labels.sort_values(by=['Community',"Hem"])
order = list(labels.index)
labels.reset_index(inplace=True,drop=True)
labels['order']=order

labels_redone = np.array([y+"_"+x for x,y in zip(np.array(labels.Community),np.array(labels.Hem))])
labels['labels']=labels_redone
labels.to_csv(GORDONLABELS)


atlasfile = "/share/sw/free/fsl/5.0.9/fsl/data/atlases/Cerebellum_MNIfnirt.xml"
cerebellum = {x:[] for x in ["label","index",'x','y','z']}
cerebellum = pd.DataFrame(cerebellum)
xmldoc = minidom.parse(atlasfile)
itemlist = xmldoc.getElementsByTagName('label')
for item in itemlist:
    label = item.childNodes[0].nodeValue
    lbs = {
        "label": label,
        "index" : int(item.getAttribute('index')),
        "x" : int(item.getAttribute('x')),
        "y" : int(item.getAttribute('y')),
        "z" : int(item.getAttribute('z'))
    }
    cerebellum = cerebellum.append(lbs,ignore_index=True)
cerebellum.to_csv(CEREBELLUMLABELS)
cerebellum['Community']='cerebellum'

atlasfile = "/share/sw/free/fsl/5.0.9/fsl/data/atlases/HarvardOxford-Subcortical.xml"
subcort = {x:[] for x in ["label","index",'x','y','z']}
subcort = pd.DataFrame(subcort)
xmldoc = minidom.parse(atlasfile)
itemlist = xmldoc.getElementsByTagName('label')
for item in itemlist:
    label = item.childNodes[0].nodeValue
    lbs = {
        "label": label,
        "index" : int(item.getAttribute('index')),
        "x" : int(item.getAttribute('x')),
        "y" : int(item.getAttribute('y')),
        "z" : int(item.getAttribute('z'))
    }
    subcort = subcort.append(lbs,ignore_index=True)
subcort.to_csv(SUBCORTLABELS)
subcort['Community']="subcortical"

labels = labels.append(subcort,ignore_index=True)
labels = labels.append(cerebellum,ignore_index=True)
for idx,row in labels.iterrows():
    if np.isnan(row['order']):
        labels = labels.set_value(idx,'order',idx)

labels.to_csv(ATLASLABELS)
