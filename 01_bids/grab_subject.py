import pandas as pd
import os

ARRAY_ID = os.environ.get("SLURM_ARRAY_TASK_ID")
participants = pd.read_csv(os.environ.get("CLEANTABLE"))
subject = participants.UID[int(ARRAY_ID)]
exit(subject)
