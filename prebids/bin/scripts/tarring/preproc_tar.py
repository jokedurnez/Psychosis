import os
import tarfile
import shutil

prepdir = os.environ.get('PREPDIR')
subs = os.listdir(prepdir)

for sub in subs:
    subdir = os.path.join(prepdir,sub)
    try:
        protocols = [x for x in os.listdir(subdir) if x.startswith('task') and not x.endswith('tar.gz')]
    except OSError:
        continue
    for protocol in protocols:
        print('tarring protocol %s in subject %s'%(sub,protocol))
        protocoldir = os.path.join(subdir,protocol)
        with tarfile.open(protocoldir+".tar.gz","w:gz") as tar:
            tar.add(protocoldir,arcname=os.path.basename(protocoldir))
        shutil.rmtree(protocoldir)
