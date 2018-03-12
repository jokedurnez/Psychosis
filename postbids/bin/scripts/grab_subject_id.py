'''
    File name: nodes.py
    Author: Joke Durnez
    Date created: 10/31/2017
    Date last modified: 10/31/2017
    Python Version: 2.7
    Description: Script to grab subject idea for use in HPC environment
    Project: Psychosis
'''

import pandas as pd
import numpy as np
import os

ARRAY_ID = os.environ.get("SLURM_ARRAY_TASK_ID")
participants = pd.read_csv(os.path.join(os.environ.get("CLEANTABLE")),sep='\t')
subject = participants.UID[int(ARRAY_ID)]
exit(subject)
