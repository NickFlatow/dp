from flask_cors import CORS, cross_origin
from flask import request
from lib.dbConn import dbConn
from lib import sasHandler
from lib.thread import lockedThread
import time

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
    SNlist = json.loads(SNlist)

    #collect all values from databse
    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist['snDict'])))
    cbsd_list = conn.select(sql,SNlist['snDict'])

    for cbsd in cbsd_list:
        if cbsd['sasStage'] != consts.REG:
            cbsd['sasStage'] = consts.REG
            conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.REG,cbsd['SN']))

    conn.dbClose()

    #create thread with threadLock so we do not get interference from heartbeat thread.
    # registrationThread = lockedThread("FeMS_reg_thread")
    
    sasHandler.Handle_Request(cbsd_list,consts.REG)

    return "success"
 
@app.route('/dp/v1/deregister', methods=['POST'])
@cross_origin()
def dp_deregister():
    #Get cbsd SNs from FeMS    
    SNlist = request.form['json']

    #convert to json
    SNlist = json.loads(SNlist)

    print(SNlist['snDict'])
    #collect all values from databse
    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist['snDict'])))
    cbsd_list = conn.select(sql,SNlist['snDict'])

    
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

    # deregistrationThread = lockedThread("FeMS_de-reg_thread")
    
    if bool(rel):
        sasHandler.Handle_Request(rel,consts.REL)
        sasHandler.Handle_Request(rel,consts.DEREG)
    if bool(dereg):
        sasHandler.Handle_Request(dereg,consts.DEREG)
    
    return "success"

@app.route('/dp/v1/reprovision', methods=['POST'])
@cross_origin()
def dp_reprovision():
    #Get cbsd SNs from FeMS    
    SNlist = request.form['json']

    #convert to json
    SNlist = json.loads(SNlist)

    #if granted relinquish grant 
    conn = dbConn(consts.DB)
    cbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",SNlist['SN'])
    

    if cbsd[0]['grantID'] != None:
        conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.REL,cbsd[0]['SN']))
        cbsd[0]['sasStage'] = consts.REL
        sasHandler.Handle_Request(cbsd,consts.REL)        

    #update cbsd sasStage for registration
    conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.REPROV,cbsd[0]['SN']))
    conn.dbClose()

    return "success"