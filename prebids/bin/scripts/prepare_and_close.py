'''
    File name: prepare_and_close.py
    Author: Joke Durnez
    Date created: 02/13/2018
    Date last modified: 02/13/2018
    Python Version: 2.7
    Description: Script to extract or compress DICOM task folders
    Project: Psychosis
'''

import argparse
import sys
import os
sys.path.append(os.environ.get("CODEDIR"))

from prebids.dicom import dicom

def get_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', dest='start', action='store_true')
    parser.add_argument('--finish', dest='finish', action='store_true')
    return parser

args = get_parser().parse_args()

if args.start:
    dicom.extract(os.environ.get("SUBJECTLABEL"))

if args.finish:
    dicom.compress(os.environ.get("SUBJECTLABEL"))
