from config.default import SAS
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
    #for cbsd in cbsd_list
        #if grantId
    sasHandler.Handle_Request(cbsd_list,consts.REL)
    sasHandler.Handle_Request(cbsd_list,consts.DEREG)
    return "success"

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
        print("registration")
        conn = dbConn("ACS_V1_1")
        cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.REG)
        conn.dbClose()
        if cbsd_list !=():
            sasHandler.Handle_Request(cbsd_list, consts.REG)

        time.sleep(30)

def heartbeat():
        while True:
            print("heartbeat")
            conn = dbConn("ACS_V1_1")
            cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.HEART)
            conn.dbClose()
            if cbsd_list !=():
                sasHandler.Handle_Request(cbsd_list,consts.HEART)
           
            time.sleep(45)    

def start():
    conn = dbConn("ACS_V1_1")
    conn.update("UPDATE dp_device_info SET sasStage = 'registration', grantID = NULL, operationalState = NULL, transmitExpireTime = NULL, grantExpireTime = NULL WHERE fccID = '2AQ68T99B226'")
    conn.dbClose()

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

def test_501_error_module():
    SNlist = ['DCE994613163']

    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist)))
    cbsd_list = conn.select(sql,SNlist)
    sasHandler.Handle_Response(cbsd_list,consts.HBE,consts.HEART)

def testUpdateGrantTime():

    conn = dbConn("ACS_V1_1")
    cbsd = conn.select("select * from dp_device_info WHERE fccID = 'FOXCONN'")
    conn.dbClose()

def setParameterValues_Test():
    conn = dbConn("ACS_V1_1")
    cbsd = conn.select("select * from dp_device_info WHERE fccID = 'FOXCONN'")
    conn.dbClose()


    EARFCN = sasHandler.MHZtoEARFCN(cbsd[0])
    print(EARFCN)

    pDict = {}
    pDict[cbsd[0]['SN']] = []
    pDict[cbsd[0]['SN']].append(consts.ADMIN_POWER_OFF)
    # pDict[cbsd[0]['SN']].append({'data_path':consts.EARFCN_LIST,'data_type':'string','data_value':EARFCN})
    # pDict[cbsd[0]['SN']].append({'data_path':consts.TXPOWER_PATH,'data_type':'int','data_value':23})

    # pDict[cbsd[0]['SN']].append({'dtat_path':})
    #add 

    # for dict in pDict[cbsd[0]['SN']]:
        # print(dict)

    sasHandler.setParameterValues(pDict,cbsd[0]['SN'])

    time.sleep(10)
    aDict = {}
    aDict[cbsd[0]['SN']] = []
    aDict[cbsd[0]['SN']].append(consts.ADMIN_POWER_ON)

    sasHandler.setParameterValues(aDict,cbsd[0]['SN'])
    # sasHandler.setParameterValue(cbsd[0]['SN'],consts.EARFCN_LIST,'string',EARFCN,1)
    # sasHandler.setParameterValue(cbsd[0]['SN'],consts.TXPOWER_PATH,'int',0,2)
    # MHz = 3585

    # EARFCN = ((MHz - 3550)/0.1) + 55240

    # print(EARFCN)


def hb_op_params_test():
    pass

def spectrum_test():

    channels = consts.FS['spectrumInquiryResponse'][0]['availableChannel']

    #show all channels
    for channel in channels:
        # for i in range(len(channel))
        print(f"low: {channel['frequencyRange']['lowFrequency']} high: {channel['frequencyRange']['highFrequency']}")
        # print(f"")

    pref = 3580000000 #middle of low and high freq from database lowFrequency + 10
    

    print('\n\n\n')
    #To convert dBm/MHz to dBm/10MHz => 37 dBm/MHz = 37 + 10 * log(10) dBm/10MHz = 47 dBm/10MHz.
    freqArray = [3560000000,3570000000,3580000000,3590000000,3600000000,3610000000,3620000000,3630000000,3640000000,3650000000.3660000000,3670000000,3680000000,3690000000]
    #check if 20MHz is avaiable
    searching = True
    while searching:
        if select_frequency(pref,channels):
            searching = False
            print("found")
        print("still searching, increase pref by 10 Mhz")
        pref = pref + 10000000
        
        # if pref ==  3690000000:
        #     pref = 3560000000
        #we have come around again and must end the loop because there is no specturm for you
    
def select_frequency(pref, channels):
    low = False
    high = False
    
    for channel in channels:
        if pref == channel['frequencyRange']['lowFrequency']:
            print(f"matched low value missing high value:")
            print(f"low: {channel['frequencyRange']['lowFrequency']} high: {channel['frequencyRange']['highFrequency']}")
            low = True
        if pref == channel['frequencyRange']['highFrequency']:
            print("matched high value missing low value:")
            print(f"low: {channel['frequencyRange']['lowFrequency']} high: {channel['frequencyRange']['highFrequency']}")
            high = True
    
        if low and high:
            #  if channel['maxEirp'] < cbsd_list[i]['maxEIRP']:
                #upate maxEirp with suggested from SAS
            return True

    return False

def change_EIRP():
    # print(consts.SPEC_EIRP)

    conn = dbConn(consts.DB)
    cbsd = conn.select("SELECT * FROM dp_device_info")
    
    channels = consts.SPEC_EIRP['spectrumInquiryResponse'][0]['availableChannel']

    for channel in channels: 
        # print(channel['lowFre'])
        if channel['frequencyRange']['lowFrequency'] == 3630000000:
            if channel['maxEirp'] < cbsd[0]['maxEIRP']:
                txPower = channel['maxEirp'] - cbsd[0]['antennaGain']
                
                print(txPower)

                pDict = {}
                pDict[cbsd[0]['SN']] = []
                pDict[cbsd[0]['SN']].append({'data_path':consts.TXPOWER_PATH,'data_type':'int','data_value':0})
                pDict[cbsd[0]['SN']].append(consts.ADMIN_POWER_OFF)
                pDict[cbsd[0]['SN']].append({'data_path':consts.EARFCN_LIST,'data_type':'string','data_value':56240})

                sasHandler.setParameterValues(pDict,cbsd[0])

                sasHandler.EARFCNtoMHZ(cbsd[0]['SN'])
                
                testCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",cbsd[0]['SN'])
                
                print("send grant request")
                print(datetime.now())
                sasHandler.Handle_Request(testCbsd,consts.GRANT)

            #SET PARAMETER VALUES SET TX POWER MAXEIRP - ANTENNA GAIN

    conn.dbClose()

def sasSpecTest():
    conn = dbConn(consts.DB)
    cbsd = conn.select("SELECT * FROM dp_device_info")
    conn.dbClose()

    # sasHandler.Handle_Response(cbsd,consts.FS,consts.SPECTRUM)

    sasHandler.Handle_Response(cbsd,consts.HB501,consts.HEART)


# start()
sasSpecTest()
# change_EIRP()
# spectrum_test()
# setParameterValues_Test()
# testUpdateGrantTime()
# test()
# test2()
# test3()
# test5()
# test5()
# test6()
# test_105_error()
# test_501_error_module()

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

