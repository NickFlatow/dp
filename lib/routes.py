from flask_cors import CORS, cross_origin
from flask import request
from lib.dbConn import dbConn
from lib import sasHandler
from lib.thread import lockedThread

from test import app

import lib.consts as consts
import json

import threading

# import threading 

# threadLock = threading.Lock()
@app.route('/', methods=['GET'])
def home():
    return"<h1>Domain Proxy</h1><p>test version</p>"

@app.route('/dp/v1/register', methods=['POST'])
@cross_origin()
def dp_register():
    
    #Get cbsd SNs from FeMS    
    SNlist = request.form['json']

    #convert to json
    SN_json_dict = json.loads(SNlist)

    #select only the values
    SNlist = list(SN_json_dict.values())
    # print(SNlist)
    # SNlist = ['DCE994613163','DCE99461317E']

    #collect all values from databse
    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist)))
    cbsd_list = conn.select(sql,SNlist)

    for cbsd in cbsd_list:
        if cbsd['sasStage'] != consts.REG:
            cbsd['sasStage'] = consts.REG
            conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.REG,cbsd['SN']))

    conn.dbClose()

    #create thread with threadLock so we do not get interference from heartbeat thread.
    # registartionThread = threadLock('FeMS_reg_thread')
    registrationThread = lockedThread("FeMS_reg_thread")
    
    registrationThread.run(cbsd_list,consts.REG)
    
    # registartionThread.join()
    # threadLock.acquire()
    # sasHandler.Handle_Request(cbsd_list,consts.REG)
    # threadLock.release()
    
    for thread in threading.enumerate(): 
        print(thread.name)
    #thread.join()

    return "success"

@app.route('/dp/v1/deregister', methods=['POST'])
@cross_origin()
def dp_deregister():
    #Get cbsd SNs from FeMS    
    SNlist = request.form['json']

    # #convert to json
    SN_json_dict = json.loads(SNlist)

    # #select only the values
    SNlist = list(SN_json_dict.values())
    # print(f"output of SNlist: {SNlist}")
    # SNlist = ['DCE994613163','DCE99461317E']

    #collect all values from databse
    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist)))
    cbsd_list = conn.select(sql,SNlist)

    
    rel = []
    dereg = []
    # print(cbsd_list)
    for cbsd in cbsd_list:
        #Relinquish grant if the cbsd is currently granted to transmit
        if cbsd['grantID'] != None:
            conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.REL,cbsd['SN']))
            cbsd['sasStage'] = consts.REL
            rel.append(cbsd)
        else:
            conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.DEREG,cbsd['SN']))
            cbsd['sasStage'] = consts.DEREG
            dereg.append(cbsd)

    conn.dbClose()
    if bool(rel):
        sasHandler.Handle_Request(rel,consts.REL)
        sasHandler.Handle_Request(rel,consts.DEREG)
    if bool(dereg):
        sasHandler.Handle_Request(dereg,consts.DEREG)
    return "success"