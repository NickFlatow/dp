import requests
import sys
from lib.db.dbConn import dbConn
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

# app = flask.Flask(__name__, instance_relative_config=True)
# app.config.from_object('config.default')
# app.config.from_pyfile('config.py')

logging.basicConfig(filename='app.log', format='%(asctime)s - %(message)s', level=logging.DEBUG)

hbtimer = 0

def contactSAS(request,method):
    # Function to contact the SAS server
    # request - json array to pass to SAS
    # method - which method SAS you would like to contact registration, spectrum, grant, heartbeat 

    return requests.post(app.config['SAS']+method, 
    cert=('certs/client.cert','certs/client.key'),
    verify=('certs/ca.cert'),
    json=request)
  
def EARFCNtoMHZ():
    # Function to convert frequency from EARFCN  to MHz 3660 - 3700
    # mhz plus 6 zeros
    # L_frq = 0
    # H_frq = 0
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT SN,cbsdId, EARFCN,lowFrequency,highFrequency FROM dp_device_info where sasStage = \'reg\''
    cbsd = conn.select(sql)

    for i in range(len(cbsd)):
        logging.info("////////////////////////////////EARFCN CONVERTION "+ cbsd[i]['SN']+"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
        print("EARFCN: " + str(cbsd[i]['EARFCN']))
        if int(cbsd[i]['EARFCN']) > 56739 or int(cbsd[i]['EARFCN']) < 55240:
            return "SPECTRUM IS OUTSIDE OF BOUNDS"
        elif cbsd[i]['EARFCN'] == 55240:
            L_frq = 3550
            H_frq = 3570
        elif cbsd[i]['EARFCN'] == 56739:
            L_frq = 3680
            H_frq = 3700
        else:
            F = math.ceil(3550 + (0.1 * (int(cbsd[i]['EARFCN']) - 55240)))
            L_frq = F - 10
            H_frq = F + 10
    
        print(L_frq,H_frq)
        
        sql = "UPDATE `dp_device_info` SET lowFrequency=\'"+str(L_frq)+"\', highFrequency=\'"+str(H_frq)+"\' WHERE SN = \'"+str(cbsd[i]['SN'])+"\'"
        conn.update(sql)        

    conn.dbClose()

def cbsdAction(cbsdSN,action,time):
    logging.info("Triggering CBSD action")
    conn = dbConn("ACS_V1_1")
    sql_action = "INSERT INTO apt_action_queue (SN,Action,ScheduleTime) values(\'"+cbsdSN+"\',\'"+action+"\',\'"+time+"\')"
    logging.info(cbsdSN + " : SQL cmd " + sql_action)
    try:
        conn.cursor.execute(sql_action)
    except Exception as e:
        logging.error(e)
    conn.dbClose()

def heartbeatResponse(cbsd):
    # print(cbsd)

    #Make connection to ACS_V1_1 database
    conn = dbConn("ACS_V1_1")
    print("response")
    for i in range(len(cbsd['heartbeatResponse'])):
        logging.info(cbsd['heartbeatResponse'][i]['cbsdId'] + ": Heartbeat Response : " + str(cbsd['heartbeatResponse'][i]))
        #if error code = 0 then process handle reply for cbsd
        # print(cbsd['heartbeatResponse'][i])
        if cbsd['heartbeatResponse'][i]['response']['responseCode'] == 0: 
        #TODO what if no reply... lost in the internet
        #TODO check if reply is recieved from all cbsds
        #TODO WHAT IF NEW OPERATIONAL PARAMS
        #TODO WHAT IF MEAS REPORT

            sql_get_op = "SELECT operationalState FROM dp_heartbeat WHERE cbsdID = \'"+cbsd['heartbeatResponse'][i]['cbsdId']+"\'"
            logging.info("SQL cmd : " + sql_get_op)
            conn.cursor.execute(sql_get_op)
            opState = conn.cursor.fetchone()
            #update operational state to granted/ what if operational state is already authorized
            sql = "UPDATE dp_heartbeat SET operationalState = CASE WHEN operationalState = 'GRANTED' THEN 'AUTHORIZED' ELSE 'AUTHORIZED' END WHERE cbsdID = \'" + cbsd['heartbeatResponse'][i]['cbsdId'] + "\'"
            #update transmist expire time
            sql1 = "UPDATE dp_heartbeat SET transmitExpireTime = \'" + cbsd['heartbeatResponse'][i]['transmitExpireTime'] + "\' where cbsdID = \'" + cbsd['heartbeatResponse'][i]['cbsdId'] + "\'"
            try:
                conn.cursor.execute(sql)
                conn.cursor.execute(sql1)
            except Exception as e:
                print(e)
            #collect SN from dp_device_info where cbsdId = $cbsdid
            if opState['operationalState'] == 'GRANTED':
                print("!!!!!!!!!!!!!!!!GRATNED!!!!!!!!!!!!!!!!!!!!!!!!")
                sql_get_sn = "SELECT `SN` FROM dp_device_info WHERE cbsdID =\'"+cbsd['heartbeatResponse'][i]['cbsdId']+"\'"
                print(sql_get_sn)
                conn.cursor.execute(sql_get_sn)
                sn = conn.cursor.fetchone()
                #turn on RF in cell
                # sql_action = "INSERT INTO apt_action_queue (SN,Action,ScheduleTime) values(\'"+sn['SN']+"\','RF_ON',\'"+str(datetime.now())+"\')"
                # conn.cursor.execute(sql_action)
                cbsdAction(sn['SN'],"RF_ON",str(datetime.now()))
            # print(sql_action)


        #if operational state  = gratned turn rf on

    #else handle error

    #close database
    conn.dbClose()

def heartbeatRequest(cbsd):
    heartbeat = {"heartbeatRequest":[]}
    print("request")
    for i in range(len(cbsd)):
        heartbeat['heartbeatRequest'].append(
                {
                    "cbsdId":cbsd[i]['cbsdID'],
                    "grantId":cbsd[i]['grantID'],
                    "operationState":cbsd[i]['operationalState']
                }
            )
        logging.info(heartbeat['heartbeatRequest'][i]['cbsdId']+ ": Heartbeat Request: " + str(heartbeat['heartbeatRequest'][i]))

    # logging.info("REQUEST FROM heartbeat: " + str(heartbeat))
    response = contactSAS(heartbeat,"heartbeat")

    heartbeatResponse(response.json())

def grantResponse(cbsd):
    #Make connection to ACS_V1_1 database
    conn = dbConn("ACS_V1_1")
    print("response")
    for i in range(len(cbsd['grantResponse'])):
        logging.info(cbsd['grantResponse'][i]['cbsdId'] + ": Grant Response : " + str(cbsd['grantResponse'][i]))
        #Check if responseCode is > 0 
        if cbsd['grantResponse'][i]['response']['responseCode'] == 0: 
            #TODO Check for measurement Report

            sql_heartbeat_update = "REPLACE INTO dp_heartbeat (`cbsdID`, `grantID`, `renewGrant`,`measReport`,`operationalState`,`grantExpireTime`) VALUES ( \'" + cbsd['grantResponse'][i]['cbsdId'] + "\' , \'" + cbsd['grantResponse'][i]['grantId'] + "\' , \'false\' , \'false\', \'GRANTED\', \'" + cbsd['grantResponse'][i]['grantExpireTime'] +"\')"
            sql_device_info_update = "update `dp_device_info` SET sasStage = 'heartbeat' where cbsdID= \'" + cbsd['grantResponse'][i]['cbsdId'] +"\'"

            try:
                # print(sql)
                conn.cursor.execute(sql_heartbeat_update)
                conn.cursor.execute(sql_device_info_update)
            except Exception as e:
                print(e)
        else:

            errorModule(response['grantResponse'][i])
    #close db connection s

    hbtimer = cbsd['grantResponse'][i]['heartbeatInterval']
    # print(hbtimer)
    conn.dbClose()
    #start spectrum inquiry

def grantRequest(cbsd):
    grant = {"grantRequest":[]}
    print("request")
    for i in range(len(cbsd)):
        grant['grantRequest'].append(
                {
                    "cbsdId":cbsd[i]['cbsdID'],
                    "operationParam":{
                        # grab antennaGain from web interface
                        "maxEirp":int(cbsd[i]['TxPower'] + cbsd[i]['antennaGain']),
                        "operationFrequencyRange":{
                            "lowFrequency":cbsd[i]['lowFrequency'] * 1000000,
                            "highFrequency":cbsd[i]['highFrequency'] * 1000000
                        }
                    }
                }
            )
        logging.info(grant['grantRequest'][i]['cbsdId']+ ": Grant Request: " + str(grant['grantRequest'][i]))



    # logging.info("REQUEST FROM GRANT: " + str(grant))
    # print(grant)
    response = contactSAS(grant,"grant")
    grantResponse(response.json())
    # logging.info("RESPONSE FROM grant REQUEST:" + response.json() )


def spectrumResponse(response):
    #make connection to domain proxy db
    conn = dbConn("ACS_V1_1")
    #for each resposne in resposne array
    for i in range(len(response['spectrumInquiryResponse'])):
        
        
        logging.info(response['spectrumInquiryResponse'][i]['cbsdId'] + ": Spec Response : " + str(response['spectrumInquiryResponse'][i]))
        
        if response['spectrumInquiryResponse'][i]['response']['responseCode'] == 0:
            # if high frequcy and low frequcy match value(convert to hz) for cbsdId in database then move to next
            low = math.floor(response['spectrumInquiryResponse'][i]['availableChannel'][0]['frequencyRange']['lowFrequency']/1000000)
            high = math.floor(response['spectrumInquiryResponse'][i]['availableChannel'][0]['frequencyRange']['highFrequency']/1000000)

            sql = "SELECT `lowFrequency`,`highFrequency` from dp_device_info where cbsdID = \'" + response['spectrumInquiryResponse'][i]['cbsdId'] + "\'"
 
 
            #if frequency if different than that requested by the cbsd. use the freqency of which was choosen by SAS and set value on cell.
 
            # try:
            #     conn.cursor.execute(sql)
            #     freq = conn.cursor.fetchall()
            # except Exception as e:
            #     print(e)

            # #if frequncy on cell is within the range of the spectrum request move to next cbsd
            # if freq[0]['lowFrequency'] < low or freq[0]['highFrequency'] > high:
            #     print("FREQUENCY ERROR!!!")
            #     #TODO if they do not match update with the range provided by SAS or just widen search
            # else:
            sqlUpdate = "update `dp_device_info` SET sasStage = 'grant' where cbsdID= \'" + response['spectrumInquiryResponse'][i]['cbsdId'] +"\'"
            conn.update(sqlUpdate)

    #TODO WHAT IF THE AVAIABLE CHANNEL ARRAY IS EMPTY
    #TODO ADD ERROR HANDELING MODULE
    
    conn.dbClose()


def spectrumRequest():

    #ADD form to the web interface to request specific spectrum in MHz. EX: 
    #get EARFCNinUSE for each cbsdID in request (TODO how to change the database to make this query more convienient)
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT cbsdId, EARFCN,lowFrequency,highFrequency FROM dp_device_info where sasStage = \'spectrum\''
    cbsd = conn.select(sql)

    spec = {"spectrumInquiryRequest":[]}

    for i in range(len(cbsd)):
        logging.info(f"/////////////////////////SPECTRUM for {cbsd[i]['cbsdId']} \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
        #build json request for SAS
        spec["spectrumInquiryRequest"].append(
            {
                "cbsdId":cbsd[i]['cbsdId'],
                "inquiredSpectrum":[
                    {
                        "highFrequency":cbsd[i]['highFrequency'] * 1000000,
                        "lowFrequency":cbsd[i]['lowFrequency']  * 1000000
                        # "highFrequency":3700 * 1000000,
                        # "lowFrequency":3590 * 1000000
                    }
                ]
            }
        )
        logging.info(spec['spectrumInquiryRequest'][i]['cbsdId']+ ": Spec Request: " + str(spec['spectrumInquiryRequest'][i]))
    
    #Send request to SAS server #contact SAS server
    # response = contactSAS(spec,"spectrumInquiry")
    response = {'spectrumInquiryResponse': [{'availableChannel': [{'channelType': 'GAA', 'ruleApplied': 'FCC_PART_96', 'frequencyRange': {'highFrequency': 3585000000, 'lowFrequency': 3565000000 } } ], 'cbsdId': 'FoxconnMock-SASDCE994613163', 'response': {'responseCode': 0} } ] }
                                                                                                                     

    # pass response to spectrum response
    # spectrumResponse(response.json())
    conn.dbClose()
    spectrumResponse(response)

def regResponse(response):
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT SN,cbsdId, EARFCN,lowFrequency,highFrequency FROM dp_device_info where sasStage = \'reg\''
    row = conn.select(sql)

    for i in range(len(response['registrationResponse'])):
        logging.info(row[i]["SN"] + ": REG Response : " + str(response['registrationResponse'][i]))
        
        #If there are no errors 
        if response['registrationResponse'][i]['response']['responseCode'] == 0: 
            #TODO Check for measurement Report

            #Update cbsdID, SAS_STAGE in device info table
            sqlUpdate = "UPDATE `dp_device_info` SET cbsdID=\""+response['registrationResponse'][i]['cbsdId']+"\",sasStage=\"spectrum\" WHERE SN=\'"+row[i]["SN"]+"\'"
            conn.update(sqlUpdate)
        else:
            errorModule(response['registrationResponse'][i])

    #close db connection
    conn.dbClose()

def regRequest():
    # COLLECT ALL DEVICES LOOKING TO BE REGISTERED
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT * FROM dp_device_info where sasStage = \'reg\''
    row = conn.select(sql)


    reg = {"registrationRequest":[]}
    
    for i in range(len(row)):
        logging.info(f"/////////////////////////REGISTRATION for {row[i]['SN']} \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
        reg['registrationRequest'].append(
                {
                    "cbsdSerialNumber": str(row[i]["SN"]),
                    "fccId": row[i]["fccID"],
                    "cbsdCategory": str(row[i]["cbsdCategory"]),
                    "userId": str(row[i]["userID"])
                }
        )
        logging.info(row[i]["SN"]+ ": Reg Request: " + str(reg['registrationRequest'][i]))
 
    # response = contactSAS(reg,"registration")
    response = {'registrationResponse': [{'cbsdId': 'FoxconnMock-SASDCE994613163', 'response': {'responseCode': 0}}]}

    conn.dbClose()
    # regResponse(response.json(),row)
    regResponse(response)


def errorModule(response):
    #add some sort of logging mechanism something like ECCLogger
    print("!!!Error!!!")
    print(response)
    print("!!!Error!!!")


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
# EARFCNtoMHZ()
# regRequest()
# spectrumRequest()


# try:
#     a_socket.connect(("192.168.4.5", 10500))
#     print("connected")
# except:
#     print("Connection failed")
#     #     conn.dbClose()

# while True:


def some_test(cbsd):
    with socket.socket() as s:
        try:
            s.connect((cbsd, 10500))
            print(f"connected to ip: {cbsd}")
        except Exception as e:
            print(f"Connection failed reason: {e}")
        time.sleep(10)
        s.close()
        print("finished")

cbsds = ["192.168.4.5", "192.168.4.9"]
for cbsd in cbsds:
    print(cbsd)
    try:
        #comma for tuple
        thread = threading.Thread(target=some_test, args=(cbsd,))
        thread.start()
    except Exception as e:
        print(f"Connection failed reason: {e}")
    

            
    #     conn = dbConn("ACS_V1_1")
    #     sql = 'SELECT cbsdId, EARFCN,lowFrequency,highFrequency FROM dp_device_info where sasStage = \'spectrum\''
    #     conn.cursor.execute(sql)
    #     spec = conn.cursor.fetchall()
    #     conn.dbClose()

    #     print("spec")
    #     logging.info("/////////////////////////SPECTRUM\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
    #     try:
    #         spectrumRequest(spec)
    #     except Exception as e:
    #         print(e)

    #     # spec = {'spectrumInquiryResponse': [{'availableChannel': [{'channelType': 'GAA', 'ruleApplied': 'FCC_PART_96', 'frequencyRange': {'highFrequency': 3570000000, 'lowFrequency': 3550000000}}], 'cbsdId': 'abc123Mock-SAS1111', 'response': {'responseCode': 0}}, {'availableChannel': [{'channelType': 'GAA', 'ruleApplied': 'FCC_PART_96', 'frequencyRange': {'highFrequency': 3700000000, 'lowFrequency': 3670000000}}], 'cbsdId': 'xyz123Mock-SAS4444', 'response': {'responseCode': 0}}]}

    #     # try:
    #     #     spectrumResponse(spec)
    #     # except Exception as e:
    #     #     print(e)

    #     conn = dbConn("ACS_V1_1")
    #     sql = 'SELECT * FROM dp_device_info where sasStage = \'grant\''
    #     conn.cursor.execute(sql)
    #     grant = conn.cursor.fetchall()
    #     conn.dbClose()

    #     print("grant")
    #     logging.info("/////////////////////////GRANT\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
    #     #TODO FINISH grantRequest
    #     try:
    #         grantRequest(grant)
    #     except Exception as e:
    #         print(e)

    #     #TODO if error break
    #     #TODO LOOP AT 80% OF heartbeat TIMER
    #     while True:
    #         # print("hb")
    #         logging.info("/////////////////////////HEARTBEAT\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
    #         conn = dbConn("ACS_V1_1")
    #         sql = 'SELECT * FROM dp_heartbeat'
    #         conn.cursor.execute(sql)
    #         hb = conn.cursor.fetchall()
    #         conn.dbClose()
    #         # print(hb)
    #         try:
    #             #TODO if grant expire time + hbinterval > datetime.now()
    #                 #print(wrong)
    #             heartbeatRequest(hb)
    #         except Exception as e:
    #             print(e)
    #             # 80% of hbtimer
    #         time.sleep(45)
    # logging.info("loop")
    # time.sleep(10)

    # hbresponse = {'heartbeatResponse': [{'grantId': '578807884', 'cbsdId': 'FoxconnMock-SASDCE994613163', 'transmitExpireTime': '2021-03-26T21:30:48Z', 'response': {'responseCode': 0}}, {'grantId': '32288332', 'cbsdId': 'FoxconMock-SAS1111', 'transmitExpireTime': '2021-03-26T21:30:48Z', 'response': {'responseCode': 0}}]}

    # try:
    #     heartbeatResponse(hbresponse)
    # except Exception as e:
    #     print(e)

    # cbsd = {'grantResponse': [{'grantExpireTime': '2021-04-02T17:08:58Z', 'grantId': '758988412', 'cbsdId': 'abc123Mock-SAS1111', 'response': {'responseCode': 0}, 'channelType': 'GAA', 'heartbeatInterval': 60}, {'grantExpireTime': '2021-04-02T17:08:58Z', 'grantId': '594127834', 'cbsdId': 'xyz123Mock-SAS4444', 'response': {'responseCode': 0}, 'channelType': 'GAA', 'heartbeatInterval': 60}]}

    # print(gres['grantResponse'][0])

    # sql = "INSERT INTO heartbeat (`cbsdID`, `grantID`, `renewGrant`,`measReport`,`operationalState`,`grantExpireTime`) VALUES ( \'" + cbsd['grantResponse'][0]['cbsdId'] + "\' , \'" + cbsd['grantResponse'][0]['grantId'] + "\' , \'false\' , \'false\', \'GRANTED\', \'" + cbsd['grantResponse'][0]['grantExpireTime'] +"\')"

    # conn = dbConn("ACS_V1_1")
    # sql = "UPDATE `dp_device_info` SET sasStage = '' WHERE sasStage = 'heartbeat'"
    # conn.cursor.execute(sql)

    # print("hbtimer",hbtimer)

    # fail = {'registrationResponse': [{'response': {'responseCode': 200}}, {'response': {'responseCode': 200}}]}
    # nonfail = {'registrationResponse': [{'cbsdId': 'abc123Mock-SAS1111', 'response': {'responseCode': 0}}, {'cbsdId': 'cde456Mock-SAS2222', 'response': {'responseCode': 0}}]}
    # regResponse(nonfail,row)
    
    # conn = dbConn("ACS_V1_1")
    # sql = "INSERT INTO dp_device_info(cbsdID,sasStage) Values(\"test\",\"testy\")"
    # conn.cursor.execute(sql)
    # conn.cursor.commit()

# app.run(port = app.config["PORT"])

