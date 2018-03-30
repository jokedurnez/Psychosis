import os
import tarfile
import shutil
from joblib import Parallel, delayed

dicomdir = os.environ.get('DICOMDIR')
subs = [x for x in os.listdir(dicomdir) if not x=='import']

def tartogethernow(sub):
    subdir = os.path.join(dicomdir,sub)
    protocols = os.listdir(subdir)
    protocols = [x for x in protocols if not x.endswith(".tar.gz")]
    for protocol in protocols:
        print('tarring protocol %s in subject %s'%(protocol,sub))
        protocoldir = os.path.join(subdir,protocol)
        with tarfile.open(protocoldir+".tar.gz","w:gz") as tar:
            tar.add(protocoldir,arcname=os.path.basename(protocoldir))
        shutil.rmtree(protocoldir)

Parallel(n_jobs=8)(delayed(tartogethernow)(sub) for sub in subs)

# # check files hwere both folder + tar exists --> indication of failed tarring
#
# k = 0
# l = 0
# for sub in subs:
#     subdir = os.path.join(dicomdir,sub)
#     protocols = os.listdir(subdir)
#     protpure = [x for x in protocols if not x.endswith(".tar.gz")]
#     k += len(protpure)
#     prottar = [x[:-7] for x in protocols if x.endswith(".tar.gz")]
#     l += len(prottar)
#     if len(set(protpure).intersection(set(prottar)))>0:
#         print(sub)
