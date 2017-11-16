import pandas as pd
import os

ARRAY_ID = os.environ.get("SLURM_ARRAY_TASK_ID")
participants = pd.read_csv(os.path.join(os.environ.get("TABLEDIR"),'REDCAP_clean.csv'))
subject = participants.UID[int(ARRAY_ID)]
exit(subject)

#print("\n".join(np.sort(participants.db_uid)))
