import requests
import sys
from lib.dbConn import dbConn
from lib.log import logger
from lib import error
from lib import sasResponseHandler
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

    #get cbsds from FeMS
    SNlist = request.form['json']
    print(f"this ist the test: {type(SNlist)}")
    #convert to json
    SN_json_dict = json.loads(SNlist)

    # SN_json_list = ",".join( map(str,SN_json_dict.values() ) )
    
    #convert to list then send to regRequest
    regRequest(list(SN_json_dict.values()))
        
    return SN_json_dict

@app.route('/dp/v1/test', methods=['POST'])
@cross_origin()
def dp_test():
    # cbsdAction('DCE994613163',"RF_ON",str(datetime.now()))
    # deregistrationRequest(('abc123','DCE994613163'))
    
    SNlist = request.form['json']
    SN_json_dict = json.loads(SNlist)
    deregistrationRequest(tuple(SN_json_dict.values()))

    #     print("!!!!!!!!!!!!!!!!!!!!!\n" + val + "\n11111111111111111111\n")
    
    return SN_json_dict

def contactSAS(request,method):
    # Function to contact the SAS server
    # request - json array to pass to SAS
    # method - which method SAS you would like to contact registration, spectrum, grant, heartbeat 
    # logger.info(f"{app.config['SAS']}  {method}")
    try:
        return requests.post(app.config['SAS']+method, 
        cert=('/home/gtadmin/dp/Domain_Proxy/certs/client.cert','/home/gtadmin/dp/Domain_Proxy/certs/client.key'),
        verify=('/home/gtadmin/dp/Domain_Proxy/certs/ca.cert'),
        json=request)
    except Exception as e:
        print(f"your connection has failed: {e}")
        return False
  
def EARFCNtoMHZ():
    # Function to convert frequency from EARFCN  to MHz 3660 - 3700
    # mhz plus 6 zeros

    conn = dbConn("ACS_V1_1")
    sql = 'SELECT SN,cbsdId, EARFCN,lowFrequency,highFrequency FROM dp_device_info where sasStage = %s'
    response = conn.select(sql,consts.REG)

    for i in range(len(response)):
        logging.info("////////////////////////////////EARFCN CONVERTION "+ response[i]['SN']+"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
        print("EARFCN: " + str(response[i]['EARFCN']))
        if int(response[i]['EARFCN']) > 56739 or int(response[i]['EARFCN']) < 55240:
            logging.info("SPECTRUM IS OUTSIDE OF BOUNDS")
            L_frq = 0
            H_frq = 0
        elif response[i]['EARFCN'] == 55240:
            L_frq = 3550
            H_frq = 3570
        elif response[i]['EARFCN'] == 56739:
            L_frq = 3680
            H_frq = 3700
        else:
            F = math.ceil(3550 + (0.1 * (int(response[i]['EARFCN']) - 55240)))
            L_frq = F - 10
            H_frq = F + 10
    
        # print(L_frq,H_frq)
        
        sql = "UPDATE `dp_device_info` SET lowFrequency=\'"+str(L_frq)+"\', highFrequency=\'"+str(H_frq)+"\' WHERE SN = \'"+str(response[i]['SN'])+"\'"
        conn.update(sql)        

    conn.dbClose()

def cbsdAction(cbsdSN,action,time):
    logging.critical("Triggering CBSD action")
    conn = dbConn("ACS_V1_1")
    sql_action = "INSERT INTO apt_action_queue (SN,Action,ScheduleTime) values(\'"+cbsdSN+"\',\'"+action+"\',\'"+time+"\')"
    logging.critical(cbsdSN + " : SQL cmd " + sql_action)
    conn.update(sql_action)
    conn.dbClose()


def heartbeatRequest():

    conn = dbConn("ACS_V1_1")
    sql_select = "SELECT * FROM dp_device_info WHERE sasStage = \'heartbeat\'"
    response = conn.select(sql_select)

    if response != ():
        heartbeat = {"heartbeatRequest":[]}
        print("hb request")
        for i in range(len(response)):
            heartbeat['heartbeatRequest'].append(
                    {
                        "cbsdId":response[i]['cbsdID'],
                        "grantId":response[i]['grantID'],
                        "operationState":response[i]['operationalState']
                    }
                )
        logger.log_json(heartbeat,len(response))
        
        response = contactSAS(heartbeat,"heartbeat")
        conn.dbClose()
        if response != False:
            sasResponseHandler.Handle_Response(response.json(),consts.HEART)
    else:
        conn.dbClose()

def grantRequest():
    #make connection to database
    conn = dbConn("ACS_V1_1")
    #select eveything where sasStage = grant
    sql_select = "select * from dp_device_info WHERE sasStage = \'grant\'"
    response = conn.select(sql_select)
    conn.dbClose()

    if response != ():
        grant = {"grantRequest":[]}
        print("grant request")
        for i in range(len(response)):
            grant['grantRequest'].append(
                    {
                        "cbsdId":response[i]['cbsdID'],
                        "operationParam":{
                            # grab antennaGain from web interface
                            "maxEirp":int(response[i]['TxPower'] + response[i]['antennaGain']),
                            "operationFrequencyRange":{
                                "lowFrequency":response[i]['lowFrequency'] * 1000000,
                                "highFrequency":response[i]['highFrequency'] * 1000000
                            }
                        }
                    }
                )
        logger.log_json(grant,len(response))
        response = contactSAS(grant,"grant")
       
        if response != False:
            sasResponseHandler.Handle_Response(response.json(),consts.GRANT)
        # logging.info("RESPONSE FROM grant REQUEST:" + response.json() )
    else:
        pass

def spectrumRequest():

    #ADD form to the web interface to request specific spectrum in MHz. EX: 
    #get EARFCNinUSE for each cbsdID in request (TODO how to change the database to make this query more convienient)
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT cbsdId, EARFCN,lowFrequency,highFrequency FROM dp_device_info where sasStage = \'spectrum\''
    response = conn.select(sql)

    if response != ():
        spec = {"spectrumInquiryRequest":[]}

        for i in range(len(response)):
            #build json request for SAS
            spec["spectrumInquiryRequest"].append(
                {
                    "cbsdId":response[i]['cbsdId'],
                    "inquiredSpectrum":[
                        {
                            "highFrequency":response[i]['highFrequency'] * 1000000,
                            "lowFrequency":response[i]['lowFrequency']  * 1000000
                            # "highFrequency":3700 * 1000000,
                            # "lowFrequency":3590 * 1000000
                        }
                    ]
                }
            )
        logger.log_json(spec,len(response))
        #Send request to SAS server #contact SAS server
        response = contactSAS(spec,"spectrumInquiry")
        # response = {'spectrumInquiryResponse': [{'availableChannel': [{'channelType': 'GAA', 'ruleApplied': 'FCC_PART_96', 'frequencyRange': {'highFrequency': 3585000000, 'lowFrequency': 3565000000 } } ], 'cbsdId': 'FoxconnMock-SASDCE994613163', 'response': {'responseCode': 0} } ] }                                                                                                       
        conn.dbClose()
        #   pass response to spectrum response
        if response != False:
            sasResponseHandler.Handle_Response(response.json(),consts.SPECTRUM)
        # spectrumResponse(response)
    else:
        conn.dbClose()

    
def regRequest(cbsds_SN = None):
    
    if cbsds_SN:
        row = query_update(cbsds_SN, consts.REG)

    else:
        conn = dbConn("ACS_V1_1")
        sql = 'SELECT * FROM dp_device_info where sasStage = \'registration\''
        row = conn.select(sql)
        conn.dbClose()

    if row != ():
        reg = {"registrationRequest":[]}
        
        for i in range(len(row)):
            reg['registrationRequest'].append(
                    {
                        "cbsdSerialNumber": str(row[i]["SN"]),
                        "fccId": row[i]["fccID"],
                        "cbsdCategory": str(row[i]["cbsdCategory"]),
                        "userId": str(row[i]["userID"])
                    }
            )
        logger.log_json(reg,len(row))
        response = contactSAS(reg,"registration")
        
        if response != False:
            sasResponseHandler.Handle_Response(response.json(),consts.REG)

        # response = {'registrationResponse': [{'cbsdId': 'FoxconnMock-SASDCE994613163', 'response': {'responseCode': 0}}]}
    else:
        pass
def deregistrationRequest(cbsds_SN = None):

    #send relinquishment
    grantRelinquishmentRequest(cbsds_SN)

    cbsd_db = query_update(cbsds_SN,'dereg')

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
    sasResponseHandler.Handle_Response(response.json(),consts.DEREG)

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
        sasResponseHandler.Handle_Response(response.json(),consts.REL)



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
    while True:
        # print(error.error_test())
        EARFCNtoMHZ()
        print("registartion")
        regRequest()
        spectrumRequest()
        grantRequest()
        time.sleep(10)

def heartbeat():
        while True:
            print("heartbeat")
            heartbeatRequest()
            #TODO dereg()
            #TODO reliquishment()
            time.sleep(4)   

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
    pass
    # regRequest()


start()
# test()

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

