import os

bidsdir = os.environ.get("BIDSDIR")
codedir = os.environ.get('CODEDIR')
#logdir = os.path.join(codedir,"prebids/bin/HPC/logs")
logdir = os.path.join(codedir,'postbids/bin/hpc/logs')

for log in os.listdir(logdir):
    if log.endswith(".err"):
        continue
    with open(os.path.join(logdir,log),'r') as fl:
        content = fl.read()
    if not 'Finished' in content:
        print("failure reported in logfile %s"%log)
