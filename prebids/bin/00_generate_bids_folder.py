'''
    File name: 00_generate_bids_folder.py
    Author: Joke Durnez
    Date created: 02/13/2018
    Date last modified: 02/13/2018
    Python Version: 2.7
    Description: Script to initiate the bids-folder (including top-level jsons)
    Project: Psychosis
'''

import sys
import os

sys.path.append(os.environ.get("CODEDIR"))

from prebids.bids import generate_json

generate_json.generate_toplevel()
