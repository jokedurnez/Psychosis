import os
import tarfile
import shutil
from joblib import Parallel, delayed

prepdir = os.environ.get('PREPDIR')
subs = os.listdir(prepdir)

def tartogethernow(sub):
    subdir = os.path.join(prepdir,sub)
    try:
        protocols = [x for x in os.listdir(subdir) if x.startswith('task') and not x.endswith('tar.gz')]
    except OSError:
        return None
    for protocol in protocols:
        print('tarring protocol %s in subject %s'%(sub,protocol))
        protocoldir = os.path.join(subdir,protocol)
        with tarfile.open(protocoldir+".tar.gz","w:gz") as tar:
            tar.add(protocoldir,arcname=os.path.basename(protocoldir))
        shutil.rmtree(protocoldir)


Parallel(n_jobs=16)(delayed(tartogethernow)(sub) for sub in subs)
