'''
    File name: XX_import_dicoms.py
    Author: Joke Durnez
    Date created: 02/13/2018
    Date last modified: 02/13/2018
    Python Version: 2.7
    Description: Script to import new dicom files (zipfiles in $DICOMDIR/import)
    Project: Psychosis
'''

import sys
import os

sys.path.append(os.path.join(os.environ.get("CODEDIR"),'prebids'))

from dicom import dicom

dicom.import_newdata(extract=True,remove=False)
