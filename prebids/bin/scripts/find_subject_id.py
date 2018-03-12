import pandas as pd
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--subject",help="subject ID",dest='subject')
args = parser.parse_args()

subjects = [args.subject]

participants = pd.read_csv(os.path.join(os.environ.get("CLEANTABLE")),sep="\t")

nums = []
for subject in list(subjects):
    idx = np.where(participants.UID==subject)[0]
    if len(idx)<1:
        raise ValueError("subject not found")
    else:
        nums.append(idx)
        print("subject ID: %i"%idx[0])

",".join([str(x) for x in np.sort([x[0] for x in nums])])
