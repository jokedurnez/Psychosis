import os
import zipfile
import numpy as np
import tarfile
import shutil

importlist = [x for x in os.listdir(os.path.join(os.environ.get("DICOMDIR"),'import')) if x.endswith("zip")]

for impfile in importlist:
    print("Currently handling zipfile: %s"%impfile)
    #impfile = 'NIDB-1380.zip'
    # extract
    print("--- ... extracting zipfile ...")
    basedir = os.path.join(os.environ.get("DICOMDIR"),'import')
    zip_ref = zipfile.ZipFile(os.path.join(basedir,impfile))
    zip_ref.extractall(os.path.join(os.environ.get("DICOMDIR"),'import'))
    #rename
    contents = [ct.filename for ct in zip_ref.filelist]
    con = [ct.split("/")[0] for ct in contents if len(ct.split("/"))==2]
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
                    #destfile = os.path.join(os.environ.get("DICOMDIR"))
        # #make tarball
        # print("--- ... making tarball ...")
        # with tarfile.open(newname+".tar.gz","w:gz") as tar:
        #     tar.add(newname,arcname=os.path.basename(newname))
        # print("--- ... removing %s"%newname)
        # #shutil.rmtree(newname)
        # print("--- ... moving to dicomdir ...")
        # os.rename("%s.tar.gz"%newname,os.path.join(os.environ.get("DICOMDIR"),"%s.tar.gz"%(cont[:-1])))
    os.remove(os.path.join(basedir,impfile))
