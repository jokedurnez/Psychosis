#!/usr/bin/env python

'''
    File name: database.py
    Author: Joke Durnez
    Date created: 02/08/2018
    Date last modified: 02/08/2018
    Python Version: 2.7
    Description: Functions to deal with DICOMs for psychosis project
    Project: Psychosis
'''

import pandas as pd
import numpy as np
import argparse
import tarfile
import zipfile
import shutil
import sys
import os
import re

def extract(subject,overwrite=False,remove_tar=True):
    '''
    Function to extract tarball with dicoms for a subjects
    :param subject: subject code (alt UID)
    :type subject: string
    :param overwrite: overwrite/add existing folder?
    :type overwrite: bool
    :param remove_tar: remove tar after extracting?
    :type remove_tar: bool
    '''
    subdicomdir = os.path.join(os.environ.get("DICOMDIR"),subject)
    tars = [x for x in os.listdir(subdicomdir) if x.endswith(".tar.gz")]
    for tar in tars:
        print(".. extracting .. %s"%tar)
        fullfolder = os.path.join(subdicomdir,tar.split('.')[0])
        fulltar = os.path.join(subdicomdir,tar)
        if os.path.exists(fullfolder) and overwrite == False:
            if remove_tar:
                os.remove(fulltar)
            continue
        zip_ref = tarfile.open(fulltar)
        zip_ref.extractall(subdicomdir)
        zip_ref.close()
        if remove_tar:
            os.remove(fulltar)

def compress(subject,overwrite=False,remove_folder=False):
    '''
    Function to compress dicoms to tarball for a subjects
    :param subject: subject code (alt UID)
    :type subject: string
    :param overwrite: overwrite/add existing tarball?
    :type overwrite: bool
    :param remove_folder: remove folder after extracting?
    :type remove_folder: bool
    '''
    subdicomdir = os.path.join(os.environ.get("DICOMDIR"),subject)
    folders = [x for x in os.listdir(subdicomdir) if not x.endswith(".tar.gz")]

    for folder in folders:
        print(".. compressing .. %s"%folder)

        tarball = os.path.join(subdicomdir,"%s.tar.gz"%folder)
        fulfolder = os.path.join(subdicomdir,folder)
        if (os.path.exists(tarball) and overwrite == True) or not os.path.exists(tarball):
            with tarfile.open(tarball,"w:gz") as tar:
                tar.add(fulfolder,arcname=os.path.basename(fulfolder))
        if overwrite == True:
            shutil.rmtree(fulfolder)

def get_protocols(subject,full=False):
    subdir = os.path.join(os.environ.get("DICOMDIR"),subject)
    SH_protocols = os.listdir(subdir)
    if full == True:
        SH_protocols = [x for x in SH_protocols]
    else:
        SH_protocols = ["_".join(x.split("_")[1:]) if x[0].isdigit() else x for x in SH_protocols]
    SH_protocols = list(np.unique(SH_protocols))
    SH_protocols = [x if not x.endswith(".tar.gz") else re.sub('.tar.gz','',x) for x in SH_protocols]
    SH_protocols = [x for x in SH_protocols if not x=='qa']
    SH_protocols = np.unique(SH_protocols).tolist()
    return SH_protocols

def _get_afni_header(scan):
    afni_cmd = "dicom_hdr %s"%scan
    out = os.popen(afni_cmd)
    outstr = out.read()
    ls = outstr.split("\n")
    return ls

def get_timetable(subject):
    '''
    Function to get a timetable for each task in the dicoms: can be helpful
    to figure out what went wrong.
    :param subject: subject code (alt UID)
    :type subject: string
    '''
    subdir = os.path.join(os.environ.get("DICOMDIR"),subject)
    extract(subject,overwrite=False,remove_tar=False)
    protocols = get_protocols(subject,full=True)
    timetable = pd.DataFrame({x:[] for x in ['protocol','time','date','scannumber']})
    for prot in protocols:
        if prot == "beh":
            continue
        protdir = os.path.join(subdir,prot)
        allfiles = [x for x in os.listdir(protdir) if not x=='qa']
        scannumber = [int(x.split("_")[2]) for x in allfiles]
        no = np.unique(scannumber)
        for scan in no:
            takescan = np.min([id for id,val in enumerate(scannumber) if val == scan])
            firstscan = allfiles[takescan]
            hdr = _get_afni_header(os.path.join(protdir,firstscan))
            # find date
            ix = ["0008 0020" in x for x in hdr]
            date = hdr[np.where(np.array(ix)==True)[0][0]].split("//")[2]
            # find time
            ix = ["0008 0031" in x for x in hdr]
            time = hdr[np.where(np.array(ix)==True)[0][0]].split("//")[2]
            newrow = {
                "protocol": prot,
                "time": time,
                "date": date,
                "scannumber": scan
            }
            timetable = timetable.append(newrow,ignore_index=True)
    timetable = timetable.sort_values(by=["date","time"])
    #compress(subject,overwrite=False,remove_folder=False)
    return timetable

def import_newdata(extract=True,remove=True):
    importlist = [x for x in os.listdir(os.path.join(os.environ.get("DICOMDIR"),'import')) if x.endswith("zip")]

    for impfile in importlist:
        basedir = os.path.join(os.environ.get("DICOMDIR"),'import')
        if extract:
            print("Currently handling zipfile: %s"%impfile)
            # extract
            print("--- ... extracting zipfile ...")
            zip_ref = zipfile.ZipFile(os.path.join(basedir,impfile))
            zip_ref.extractall(os.path.join(os.environ.get("DICOMDIR"),'import'))
            #rename
            contents = [ct.filename for ct in zip_ref.filelist]
            con = [ct.split("/")[0] for ct in contents if len(ct.split("/"))==2]
        elif not extract:
            con = os.listdir(contents)
        for cont in con:
            if len(cont)>8:
                print("--- ... renaming folders ...")
                newname = os.path.join(os.environ.get("DICOMDIR"),cont[:-1])
                if not os.path.exists(newname):
                    os.rename(os.path.join(basedir,cont),newname)
                else:
                    for path,dirs,files in os.walk(os.path.join(basedir,cont)):
                        if path.endswith("qa") or path.endswith("json") or path.endswith('js'):
                            continue
                        newdir = "_".join(path.split("_")[1:])
                        destdir = os.path.join(os.environ.get("DICOMDIR"),cont[:-1],newdir)
                        if not os.path.exists(destdir):
                            os.mkdir(destdir)
                        for dcmfile in files:
                            destfile = os.path.join(destdir,dcmfile)
                            oldfile = os.path.join(path,dcmfile)
                            if not os.path.exists(destfile):
                                os.rename(oldfile,destfile)
            rename_dicomdirs(cont[:-1])
        if remove:
            os.remove(os.path.join(basedir,impfile))

def rename_dicomdirs(UID):
    subdicomdir = os.path.join(os.environ.get("DICOMDIR"),UID)
    conts = os.listdir(subdicomdir)
    for cont in conts:
        try:
             integer = int(cont.split("_")[0])
        except ValueError:
            continue
        oldname = os.path.join(subdicomdir,cont)
        newname = os.path.join(subdicomdir,"_".join(cont.split("_")[1:]))
        if not os.path.exists(newname):
            os.rename(oldname,newname)
        else:
            for path,dirs,files in os.walk(oldname):
                if path.endswith("qa") or path.endswith("json") or path.endswith('js'):
                    continue
                for dcmfile in files:
                    destfile = os.path.join(newname,dcmfile)
                    oldfile = os.path.join(oldname,dcmfile)
                    if not os.path.exists(destfile):
                        os.rename(oldfile,destfile)
            shutil.rmtree(oldname)
