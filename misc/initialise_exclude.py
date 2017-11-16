import json
import pandas as pd
import os

with open(os.environ.get("EXCLUSIONTABLE"),'r') as fl:
    data = json.load(fl)

EXDB = pd.DataFrame(data)

dealtwith = [ "S2289PGV","S3847DYG","S1377DEU","S0045WGH","S6359VVT","S6108RVJ","S1218UVF","S0446XAR","S4324REV","S2045YOJ",'S8048ECC','S2108OWF','S6020NDB',"S0851CAY","S0509PIJ","S4446TOP","S1772MFS","S3479LVP","S1078JSG","S2673YWR","S8237AHJ",'S5839CPU','S3232XVO',"S0904OHA",'S1077DHI']

for dw in dealtwith:
    dwid = np.where(EXDB.UID==dw)[0][0]
    EXDB = EXDB.set_value(dwid,'action','double scan removed')
    EXDB = EXDB.set_value(dwid,'exclude',False)

ignore = [ "S9905QEN","S8886NLT","S2800WSU","S3543JIU","S2059FAY","S1543TWL","S4277MYS","S4428VOX","S6716YSQ","S6027QUG","S1318RPT","S2119LAL","S9245RYS","S7213UYR","S9821QYY","S8337TOX","S8555KAD","S9608MSH","S3613IXV","S1802COF","S5332RML","S5491MQQ","S4677LFE","S6954XGJ","S0924OXW","S4574FRF","S4654USL","S1427XBN","S0056GHW","S8692WOH","S5048OYI","S6850DQF","S8843FXP","S8199BBI","S0576VBM","S5060SYI","S8315JKG","S9368OMW","S2499DRQ","S9992POE","S3641CGP","S1406LMM","S5171RCJ","S3911OYN","S6463DJD","S7189DXX","S6226TYN","S0492QGT","S6450UUI","S1455AYX","S7090NWW","S1197RDU","S5555OJD","S2232WAX","S9077TOY","S0497TVN","S3840VML","S6477YYO","S2213FRB","S6751CLT","S8933FQK","S5067CIG","S1370ERP","S8364AVD"]

for ig in ignore:
    igid = np.where(EXDB.UID==ig)[0][0]
    EXDB = EXDB.set_value(igid,'action','ignored')
    EXDB = EXDB.set_value(igid,'exclude',False)

exclude = ["S2501LHE","S9047GKW"]

for ex in exclude:
    exid = np.where(EXDB.UID==ex)[0][0]
    EXDB = EXDB.set_value(exid,'action','problem in note')


EXDB = EXDB.T.to_dict().values()

with open(os.environ.get("EXCLUSIONTABLE"),'w') as fl:
    json.dump(EXDB,fl)
