import os
import tarfile
import shutil

dicomdir = os.environ.get('DICOMDIR')
subs = [x for x in os.listdir(dicomdir) if not x=='import']

for sub in subs:
    subdir = os.path.join(dicomdir,sub)
    protocols = os.listdir(subdir)
    protocols = [x for x in protocols if not x.endswith(".tar.gz")]
    for protocol in protocols:
        print('tarring protocol %s in subject %s'%(protocol,sub))
        protocoldir = os.path.join(subdir,protocol)
        with tarfile.open(protocoldir+".tar.gz","w:gz") as tar:
            tar.add(protocoldir,arcname=os.path.basename(protocoldir))
        shutil.rmtree(protocoldir)
