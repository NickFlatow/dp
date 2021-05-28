import requests
import sys
from lib.dbConn import dbConn
from lib.log import logger
from lib import error
from lib import sasHandler
from test import app, runFlaskSever
import json
import flask
from flask import request
import math
import time
from datetime import datetime
from datetime import timedelta
import logging
import socket
import threading
import lib.consts as consts
from flask_cors import CORS, cross_origin
from itertools import filterfalse

#init log class
logger = logger()
hbtimer = 0


def test():
    pass
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
    print(SNlist)

    #collect all values from databse
    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist)))
    cbsd_list = conn.select(sql,SNlist)

    sasHandler.Handle_Request(cbsd_list,consts.REG)
    return "success"

@app.route('/dp/v1/test', methods=['POST'])
@cross_origin()
def dp_deregister():
    #Get cbsd SNs from FeMS    
    SNlist = request.form['json']

    #convert to json
    SN_json_dict = json.loads(SNlist)

    #select only the values
    SNlist = list(SN_json_dict.values())
    # print(SNlist)

    #collect all values from databse
    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist)))
    cbsd_list = conn.select(sql,SNlist)

    print(cbsd_list)
    sasHandler.Handle_Request(cbsd_list,consts.REL)
    sasHandler.Handle_Request(cbsd_list,consts.DEREG)
    return "success"

def deregistrationRequest(cbsds_SN = None):

    #send relinquishment
    grantRelinquishmentRequest(cbsds_SN)

    cbsd_db = query_update(cbsds_SN,consts.DEREG)

    #send deregistration
    dereg = {"deregistrationRequest":[]}
    for i in range(len(cbsd_db)):
        #power off RF(How do I know if the CBSD turned off ADMIN_STATE check? do I still need to socket test?)
        cbsdAction(cbsd_db[i]['SN'],"RF_OFF",str(datetime.now()))

        #build json request for SAS
        dereg["deregistrationRequest"].append(
            {
                "cbsdId":cbsd_db[i]['cbsdID'],
            }
        )
    logger.log_json(dereg,len(cbsd_db))
    response = contactSAS(dereg,consts.DEREG)
    sasHandler.Handle_Response(response.json(),consts.DEREG)

def grantRelinquishmentRequest(cbsd_SN_list):
    #select all cbsds looking to have grant relinquished and updatea their status
    cbsds = query_update(cbsd_SN_list,'relinquish')
    
    #build reliquishment array
    relinquish = {"relinquishmentRequest":[]}
    for response in cbsds:
        # print(response['userID'])
        relinquish["relinquishmentRequest"].append(
            {
                "cbsdId":response['cbsdID'],
                "grantId":response['grantID']
            }
        )
    
    logger.log_json(relinquish,len(cbsds))
    
    #set grant IDs to NULL
    conn = dbConn("ACS_V1_1")
    update_grantID = "UPDATE dp_device_info SET grantID = NULL WHERE SN in" + str(cbsd_SN_list) + ";"
    
    logging.info(f"\n grant ID = NULL: {update_grantID} ")
    conn.update(update_grantID)
    conn.dbClose()
    
    #send request to SAS
    response = contactSAS(relinquish,"relinquishment")
    
    #process reponse
    if response != False:
        sasHandler.Handle_Response(response.json(),consts.REL)



def getResponseType(sasStage):
    if sasStage == 'reg':
        return 'registartionResponse'


def query_update(cbsds_SN_list,sasStage):
    conn = dbConn("ACS_V1_1")
    sql_select = 'SELECT * FROM dp_device_info WHERE SN IN ({})'.format(','.join(['%s'] * len(cbsds_SN_list)))
    rows = conn.select(sql_select,cbsds_SN_list)
    print(rows)
    conn.updateSasStage(sasStage,cbsds_SN_list)
    conn.dbClose()
    return rows


def expired(time):
    #convert sting to datetime and compare to current time.
    hbinterval = 60
    hbresponse = {'heartbeatResponse': [{'grantId': '578807884', 'cbsdId': 'FoxconnMock-SASDCE994613163', 'transmitExpireTime': '2021-04-9T18:01:48Z', 'response': {'responseCode': 0}}, {'grantId': '32288332', 'cbsdId': 'FoxconMock-SAS1111', 'transmitExpireTime': '2021-03-26T21:30:48Z', 'response': {'responseCode': 0}}]}
    # print(hbresposne['hearbeatResposne'][i]['transmitExpireTime'])
    
    #time of which grant or transmit will expire
    expireTime = datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ")
    print(expireTime)
    timeChange = expireTime + timedelta(seconds=hbinterval)
    print(datetime.now())
    print(timeChange)
    #if the current time is less than the expire time plus the heartbeat interval
    if timeChange > datetime.now():
        try:
            conn = dbConn("ACS_V1_1")
            sql = "UPDATE `dp_device_info` SET `sasStage` = 'dereg' where `cbsdID` = 'FoxconnMock-SASDCE994613163'"
            conn.cursor.execute(sql)
            cbsdAction("DCE994613163","RF_OFF",str(datetime.now()))
        except Exception as e:
            print(e)
    else:
        return False

print(__name__) 

# while True:  
    # app.run(port = app.config["PORT"])

    # cbsdAction("DCE994613163","RF_OFF",str(datetime.now()))
    # EARFCNtoMHZ([{'EARFCN':55240},{'EARFCN':55990},{'EARFCN':56739}])
    
    #Convert EARFCN into hz

def registration():
    meth = [consts.REG,consts.SPECTRUM,consts.GRANT]

    while True:
        # for m in meth:
        conn = dbConn("ACS_V1_1")
        cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.REG)
        conn.dbClose()
        if cbsd_list !=():
            sasHandler.Handle_Request(cbsd_list, consts.REG)

        time.sleep(30)

def heartbeat():
        while True:
            conn = dbConn("ACS_V1_1")
            cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.HEART)
            conn.dbClose()
            if cbsd_list !=():
                sasHandler.Handle_Request(cbsd_list,consts.HEART)
           
            time.sleep(5)   

def start():
    try:
        #if using args a comma for tuple is needed 
        thread = threading.Thread(target=registration, args=())
        thread.start()
    except Exception as e:
        print(f"Registration thread failed: {e}")
    try:
        #if using args a comma for tuple is needed 
        thread = threading.Thread(target=heartbeat, args=())
        thread.start()
    except Exception as e:
        print(f"Heartbeat thread failed reason: {e}")
    runFlaskSever()


def test():
    # error_resposne = {"registrationResponse": [{"response": {"responseCode": 200}},{"response": {"responseCode": 200}}]}
    # error_response =  {"registrationResponse": [{"response": {"responseCode": 200,"responseMessage": "A Category B device must be installed by a CPI"}}]}

    meth = [consts.REG,consts.SPECTRUM,consts.GRANT]

    while True:
        for m in meth:
            conn = dbConn("ACS_V1_1")
            cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',m)
            conn.dbClose()
            if cbsd_list !=():
                sasHandler.Handle_Request(cbsd_list, m)

        time.sleep(20)
        # regRequest()

def test2():
    SNlist = str({"SN1":"DCE994613163","SN2":"abc123"})

    # print(SNlist)
    # SN_json_dict = json.loads(SNlist)
    # print(SN_json_dict)

    SN_json_dict = {'SN1': 'DCE994613163', 'SN2': 'abc123'}


    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(list(SN_json_dict.values()))))
    cbsd_list = conn.select(sql,list(SN_json_dict.values()))

    # sasHandler.Handle_Request(cbsd_list,consts.REG)
    print(type(cbsd_list))

def test3():
    erroDict = {'DCE994613163': "has error", 'abc123': "has error"}

    conn = dbConn("ACS_V1_1")
    cbsd_list = conn.select("SELECT * FROM dp_device_info WHERE sasStage = %s","NONE")
    cbsd_list[:] = [cbsd for cbsd in cbsd_list if not hasError(cbsd,erroDict)]

    print(bool(cbsd_list))

def test4(): 
    
    SNlist = ['abc123','DCE994613163']

    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist)))
    cbsd_list = conn.select(sql,SNlist)

    print(cbsd_list)
    sasHandler.Handle_Request(cbsd_list,consts.REL)
    sasHandler.Handle_Request(cbsd_list,consts.DEREG)

def test5():
    
    SNlist = ['DCE994613163']

    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist)))
    cbsd_list = conn.select(sql,SNlist)

    sasHandler.Handle_Request(cbsd_list,consts.SPECTRUM)
def test6():

    sasHandler.setParameterValue("DCE994613163",consts.TXPOWER_PATH,"int",5)

def test_105_error():
    errorDict = {'DCE994613163': {'responseCode': 105}}
    error.errorModule(errorDict,consts.REG)




start()
# test()
# test2()
# test3()
# test5()
# test5()
# test6()
# test_105_error()

# try:
#     a_socket.connect(("192.168.4.5", 10500))
#     print("connected")
# except:
#     print("Connection failed")
#     #     conn.dbClose()

# while True:


# def some_test(response):
#     with socket.socket() as s:
#         try:
#             s.connect((response, 10500))
#             print(f"connected to ip: {response}")
#         except Exception as e:
#             print(f"Connection failed reason: {e}")
#         time.sleep(10)
#         s.close()
#         print("finished")

# cbsds = ["192.168.4.5", "192.168.4.9"]
# for response in cbsds:
#     print(response)
#     try:
#         #comma for tuple
#         thread = threading.Thread(target=some_test, args=(response,))
#         thread.start()
#     except Exception as e:
#         print(f"Connection failed reason: {e}")

