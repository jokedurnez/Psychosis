#!/usr/bin/python2
import os
for par, dirs, files in os.walk(os.environ.get("BIDSDIR")):
    print(par)
    if par.startswith(os.path.join(os.environ.get("BIDSDIR"),'derivatives/')):
        for d in dirs:
            os.chmod(par + '/' + d, 0770)
        for f in files:
            os.chmod(par + '/' + f, 0660)
    else:
        for d in dirs:
            os.chmod(par + '/' + d, 0550)
        for f in files:
            os.chmod(par + '/' + f, 0440)
