import os

BIDSDIR = os.environ['BIDSDIR']
ID = os.environ['SUBJECTLABEL']

subdir = 'sub-'+str(ID)
if os.path.isdir(os.path.join(BIDSDIR, subdir)):
    pass
elif os.path.isdir(os.path.join(BIDSDIR, str(ID))):
    os.rename(os.path.join(BIDSDIR, str(ID)),
              os.path.join(BIDSDIR, subdir))
else:
    raise ValueError("Can't find a folder for subject "+str(SUBJECTLABEL))

direc = os.path.join(BIDSDIR, subdir)

# discard rest run 2 and 3
IDs = ["S2045YOJ"]
if ID in IDs:
    runs = [2,3]
    for run in runs:
        func_base = direc+"/func/sub-"+ID+"_task-rest_acq-LR_run-"+str(run)
        ext = ["_sbref.json","_sbref.nii.gz","_bold.json","_bold.nii.gz"]
        for e in ext:
            os.remove(func_base+e)

IDs = ["S2289PGV"]
if ID in IDs:
    run = 2
    func_base = direc+"/func/sub-"+ID+"_task-rest_acq-LR_run-"+str(run)
    ext = ["_sbref.json","_sbref.nii.gz","_bold.json","_bold.nii.gz"]
    for e in ext:
        os.remove(func_base+e)


IDs = ["S1772MFS"]
if ID in IDs:
    run = 2
    func_base = direc+"/func/sub-"+ID+"_task-rest_acq-RL_run-"+str(run)
    ext = ["_sbref.json","_sbref.nii.gz","_bold.json","_bold.nii.gz"]
    for e in ext:
        os.remove(func_base+e)

# discard rest run 1
IDs = ["S3847DYG"]
if ID in IDs:
    run = 1
    func_base = direc+"/func/sub-"+ID+"_task-rest_acq-RL_run-"+str(run)
    ext = ["_sbref.json","_sbref.nii.gz","_bold.json","_bold.nii.gz"]
    for e in ext:
        os.remove(func_base+e)


# discard first T1
IDs = ["S1377DEU","S0045WGH","S6359VVT","S0851CAY","S6108RVJ","S1218UVF","S0446XAR","S4324REV","S2045YOJ",'S5839CPU',"S0904OHA",'S8048ECC','S2108OWF','S6020NDB','S8499STQ']
if ID in IDs:
    run = 1
    T1_base = direc+"/anat/sub-"+ID+"_run-%i_T1w"%run
    ext = [".json",".nii.gz"]
    for e in ext:
        os.remove(T1_base+e)

# discard first T2
IDs = ["S0851CAY","S6108RVJ","S0509PIJ","S4446TOP","S1772MFS","S3479LVP","S1078JSG","S2673YWR","S8237AHJ",'S5839CPU','S3232XVO',"S0904OHA",'S1077DHI']
if ID in IDs:
    for run in [1,2]:
        if run==2 and not ID == "S0509PIJ":
            continue #i.e. only for PIJ 2 runs
        print(direc)
        print(ID)
        T2_base = str(direc)+"/anat/sub-"+str(ID)+"_run-%i_T2w"%run
        ext = [".json",".nii.gz"]
        for e in ext:
            os.remove(T2_base+e)
