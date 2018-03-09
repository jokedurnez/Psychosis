import os
import numpy as np
import pandas as pd
import sys

subid = sys.argv[1]
dicomdir = os.environ.get("DICOMDIR")
subdir = dicomdir+subid
protocols = os.listdir(subdir)

prots = []
timess = []
datess = []
nums = []

for prot in protocols:
    #print(prot)
    if prot == "beh":
        continue
    protdir = subdir+"/"+prot
    allfiles = os.listdir(protdir)
    numbers = [x[11:13] for x in allfiles]
    no = np.unique(numbers)[1:]
    times = []
    dates = []
    for scan in no:
        takescan = np.min([id for id,val in enumerate(numbers) if val == scan])
        file = allfiles[takescan]
        if file == "qa":
            continue
        afni_cmd = "dicom_hdr "+protdir+"/"+file
        out = os.popen(afni_cmd)
        outstr = out.read()
        ls = outstr.split("\n")
        ix = ["0008 0020" in x for x in ls]
        date = ls[np.where(np.array(ix)==True)[0][0]].split("//")[2]
        ix = ["0008 0031" in x for x in ls]
        time = ls[np.where(np.array(ix)==True)[0][0]].split("//")[2]
        times.append(float(time[:-1]))
        dates.append(int(date[:-1]))
    timess = timess+np.unique(times).tolist()
    prots = prots+[prot]*len(np.unique(times))
    datess = datess+[np.unique(dates).tolist()[0]]*len(np.unique(times))
    nums = nums+no.tolist()

DF = pd.DataFrame({"protocol":prots,"time":timess,"date":datess,"scannumber":nums})
DF = DF.sort_values(by=["date","time"])

print(DF)
