import json
import os

out = []
for idx,row in DB.iterrows():
    RCid = np.where(row.AltStudyID==RC.scan_id)[0]
    if len(RCid)>0:
        note = RC.if_there_are_repeated_scan[RCid[0]]
        if (type(note)==str and len(note)>0):
            adrow = {
                "note":note,
                "exclude":True,
                "scan_id":row.AltStudyID,
                "RC_id":RC.subject_id[RCid[0]],
                "UID":row.UID,
                "action":"not handled yet"
            }
            out.append(adrow)

excludefile = os.environ.get("EXCLUSIONTABLE")
os.remove(excludefile)
with open(excludefile,"w") as fl:
    json.dump(out,fl)
