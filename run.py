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
from requests.auth import HTTPDigestAuth

#needed here to make routes work
from lib import routes

#init log class
logger = logger()
hbtimer = 0
#create threadLock
threadLock = threading.Lock()

def registration():
    meth = [consts.REG,consts.SPECTRUM,consts.GRANT]

    while True:
        # for m in meth:
        print("registration")
        conn = dbConn("ACS_V1_1")
        cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.PROV_REG)
        conn.dbClose()
        if cbsd_list !=():
            sasHandler.Handle_Request(cbsd_list, consts.REG)

        time.sleep(30)

def heartbeat():
        while True:
            threadLock.acquire()
            print("heartbeat")
            conn = dbConn("ACS_V1_1")
            cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.HEART)
            conn.dbClose()
            if cbsd_list !=():
                sasHandler.Handle_Request(cbsd_list,consts.HEART)
               
            threadLock.release()
            time.sleep(3)    

def start():
    # conn = dbConn("ACS_V1_1")
    # conn.update("UPDATE dp_device_info SET sasStage = 'registration', grantID = NULL, operationalState = NULL, transmitExpireTime = NULL, grantExpireTime = NULL WHERE fccID = '2AQ68T99B226'")
    # conn.dbClose()
    try:
        #if using args a comma for tuple is needed 
        thread = threading.Thread(target=registration, args=())
        thread.name = 'registration-thread'
        thread.start()
    except Exception as e:
        print(f"Registration thread failed: {e}")
    try:
        #if using args a comma for tuple is needed 
        hbthread = threading.Thread(target=heartbeat, args=())
        hbthread.name = 'heartbeat-thread'
        hbthread.start()

    except Exception as e:
        print(f"Heartbeat thread failed reason: {e}")
    runFlaskSever() 


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
            # if channel['maxEirp'] < cbsd[0]['maxEIRP']:
                txPower = channel['maxEirp'] - cbsd[0]['antennaGain']
                
                print(txPower)

                pDict = []
                pDict.append({'data_path':consts.TXPOWER_PATH,'data_type':'int','data_value':10})
                pDict.append(consts.ADMIN_POWER_OFF)
                pDict.append({'data_path':consts.EARFCN_LIST,'data_type':'string','data_value':55590})

                sasHandler.setParameterValues(pDict,cbsd[0])

                # sasHandler.EARFCNtoMHZ(cbsd[0]['SN'])
                
                # testCbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",cbsd[0]['SN'])
                
                # print("send grant request")
                # print(datetime.now())
                # sasHandler.Handle_Request(testCbsd,consts.GRANT)

            #SET PARAMETER VALUES SET TX POWER MAXEIRP - ANTENNA GAIN

    conn.dbClose()

def sasSpecTest():


    conn = dbConn(consts.DB)
    # g = conn.select("SELECT getValue FROM fems_gpv WHERE SN = %s", 'DCE994613163')
    cbsd = conn.select("SELECT * FROM dp_device_info")
    conn.dbClose()

  
    sasHandler.Handle_Response(cbsd,consts.FS,consts.SPECTRUM)

    # sasHandler.Handle_Response(cbsd,consts.HB501,consts.HEART)
    
    # g =sasHandler.getParameterValue('Device.X_FOXCONN_FAP.CellConfig.EUTRACarrierARFCNDL',cbsd[0])


def getParameters(cbsd):
    conn = dbConn(consts.DB)
    
    #collect all parameters from subscription table (update to json ajax send or add more value so there is no case of duplicated entires with same SN in apt_subscription table)
    parameters = conn.select("SELECT parameter FROM apt_subscription WHERE SN = %s",cbsd['SN'])
    
    #convert to json
    parameters = json.loads(parameters[0]['parameter'])
    
    #get eutra values(all possible earfcns provided by user in the subscription table)
    eutra = parameters['EUTRACarrierARFCNDL']['value']
    
    #convert to list
    earfcnList = list(eutra.split(","))

    #convert all values to ints
    earfcnList = [int(i) for i in earfcnList]

    for i in earfcnList:
        print(i)
        print(type(i))
        
    #get current earfcn in use(currently assigned to the cell from SON) 
    earfcn = conn.select("SELECT EARFCN FROM dp_device_info WHERE SN = %s",cbsd['SN'])
    #add to the front of the list
    earfcnList.insert(0,earfcn[0]['EARFCN'])

    conn.dbClose()

    return earfcnList

def powerOn():

    conn = dbConn(consts.DB)
    cbsd =conn.select("SELECT * FROM dp_device_info")
    conn.dbClose()

    pList = []
    for c in cbsd:
        # response = requests.get(c['connreqURL'], auth= HTTPDigestAuth(c['connreqUname'],c['connreqPass']))
        # print(response)
        pList.append(consts.ADMIN_POWER_ON)
        # pList.append(consts.ADMIN_POWER_ON)
        sasHandler.setParameterValues(pList,c)

def test_dereg(): 
    dp_deregister()

def error_106():
    conn = dbConn(consts.DB)
    cbsds = conn.select("SELECT * FROM dp_device_info")
    conn.dbClose()
    sasHandler.Handle_Response(cbsds, consts.ERR106,consts.GRANT)

def error_501():
    conn = dbConn(consts.DB)
    cbsds = conn.select("SELECT * FROM dp_device_info")
    conn.dbClose()
    sasHandler.Handle_Response(cbsds, consts.ERR501,consts.HEART)


start()
# error_501()
# error_106()
# test_dereg()
# powerOn()
# getParameters()
# sasSpecTest()
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
