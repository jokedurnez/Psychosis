import pandas as pd
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--subject",help="subject ID",dest='subject')
args = parser.parse_args()

if args.subject:
    ARRAY_ID = args.subject
else:
    ARRAY_ID = os.environ.get("SLURM_ARRAY_TASK_ID")

participants = pd.read_csv(os.path.join(os.environ.get("CLEANTABLE")),sep="\t")
subject = participants.UID[int(ARRAY_ID)]
exit(subject)
