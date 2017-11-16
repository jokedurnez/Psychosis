import utils.psydb as psydb
import utils.psyrc as psyrc
import utils.psy as psy
import pandas as pd
import numpy as np
import os

# read in redcap and nidb
DB = pd.read_csv(os.environ.get("NIDBTABLE"))
DB = psydb.clean_DB(DB)
DB.to_csv(os.environ.get("NIDBcleanTABLE"))

dicoms = [x[:8] for x in os.listdir(os.environ.get("DICOMDIR"))]

sh_mis = set(DB.UID)-set(dicoms)
sh_mis_str = ",".join(list(sh_mis))
print("The following subjects are missing on sherlock and should be downloaded: \n%s"%sh_mis_str)
