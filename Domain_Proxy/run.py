import requests
import sys
from lib.db.dbConn import dbConn
from lib.log.log import logger
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
    # cbsdAction('DCE994613163',"RF_ON",str(datetime.now()))
    # deregistrationRequest(('abc123','DCE994613163'))
    # print(f"{request.form['json']}")
    SNlist = request.form['json']
    SN_json_dict = json.loads(SNlist)
    regRequest(tuple(SN_json_dict.values()))

    # for val in SN_json_dict.values():
    #     print("!!!!!!!!!!!!!!!!!!!!!\n" + val + "\n11111111111111111111\n")
        
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
    logging.critical("Triggering CBSD action")
    conn = dbConn("ACS_V1_1")
    sql_action = "INSERT INTO apt_action_queue (SN,Action,ScheduleTime) values(\'"+cbsdSN+"\',\'"+action+"\',\'"+time+"\')"
    logging.critical(cbsdSN + " : SQL cmd " + sql_action)
    conn.update(sql_action)
    conn.dbClose()

def heartbeatResponse(cbsd):
    # cbsd is the response from the SAS for the preceding heartbeat request

    print("hb response")

    #add cbsd heartbeat response to log file
    logger.log_json(cbsd,len(cbsd['heartbeatResponse']))
    for i in range(len(cbsd['heartbeatResponse'])):
        #Make connection to ACS_V1_1 database
        conn = dbConn("ACS_V1_1")
        sql_select_all = "SELECT * FROM dp_device_info WHERE cbsdID = %s"
        #select everything from the database where cbsdID = cbsdId from heartbeat response
        cbsd_db = conn.select(sql_select_all,cbsd['heartbeatResponse'][i]['cbsdId'])
        
        
        
        
        #TODO WHAT IF NEW OPERATIONAL PARAMS(HANDLE THIS IN ERROR HANDLE MODULE)

        #if error code = 0 then process handle reply for cbsd
        if cbsd['heartbeatResponse'][i]['response']['responseCode'] == 0: 
        #TODO what if no reply... lost in the internet
        #TODO check if reply is recieved from all cbsds
        #TODO WHAT IF MEAS REPORT
        #TODO
            #update operational state to granted/ what if operational state is already authorized
            update_operational_state = "UPDATE dp_device_info SET operationalState = CASE WHEN operationalState = 'GRANTED' THEN 'AUTHORIZED' ELSE 'AUTHORIZED' END WHERE cbsdID = \'" + cbsd['heartbeatResponse'][i]['cbsdId'] + "\'"
            conn.update(update_operational_state)
            #update transmist expire time
            update_transmit_time = "UPDATE dp_device_info SET transmitExpireTime = \'" + cbsd['heartbeatResponse'][i]['transmitExpireTime'] + "\' where cbsdID = \'" + cbsd['heartbeatResponse'][i]['cbsdId'] + "\'"
            conn.update(update_transmit_time)
            conn.dbClose()

            #collect SN from dp_device_info where cbsdId = $cbsdid
            if cbsd_db[0]['operationalState'] == 'GRANTED':
                print("!!!!!!!!!!!!!!!!GRATNED!!!!!!!!!!!!!!!!!!!!!!!!")
                # turn on RF in cell
                cbsdAction(cbsd_db[0]['SN'],"RF_ON",str(datetime.now()))
    
        else:
            #close database
            conn.dbClose()
            #handle error

        #if operational state  = gratned turn rf on

def heartbeatRequest():

    conn = dbConn("ACS_V1_1")
    sql_select = "SELECT * FROM dp_device_info WHERE sasStage = \'heartbeat\'"
    cbsd = conn.select(sql_select)

    if cbsd != ():
        heartbeat = {"heartbeatRequest":[]}
        print("hb request")
        for i in range(len(cbsd)):
            heartbeat['heartbeatRequest'].append(
                    {
                        "cbsdId":cbsd[i]['cbsdID'],
                        "grantId":cbsd[i]['grantID'],
                        "operationState":cbsd[i]['operationalState']
                    }
                )
        logger.log_json(heartbeat,len(cbsd))
        
        response = contactSAS(heartbeat,"heartbeat")
        conn.dbClose()
        if response != False:
            heartbeatResponse(response.json())
    else:
        conn.dbClose()

def grantResponse(cbsd):
    #Make connection to ACS_V1_1 database
    conn = dbConn("ACS_V1_1")
    print("grant response")

    #log reponse
    logger.log_json(cbsd,len(cbsd['grantResponse']))

    for i in range(len(cbsd['grantResponse'])):
        
        #Check if responseCode is > 0 
        if cbsd['grantResponse'][i]['response']['responseCode'] == 0: 
            #TODO Check for measurement Report

            # sql_heartbeat_update = "REPLACE INTO dp_heartbeat (`cbsdID`, `grantID`, `renewGrant`,`measReport`,`operationalState`,`grantExpireTime`) VALUES ( \'" + cbsd['grantResponse'][i]['cbsdId'] + "\' , \'" + cbsd['grantResponse'][i]['grantId'] + "\' , \'false\' , \'false\', \'GRANTED\', \'" + cbsd['grantResponse'][i]['grantExpireTime'] +"\')"
            sql_update = "UPDATE `dp_device_info` SET `grantID` = %s , `grantExpireTime` = %s, `operationalState` = \'GRANTED\', `sasStage` = \'heartbeat\' WHERE `cbsdID` = %s"

            conn.update(sql_update,(cbsd['grantResponse'][i]['grantId'],cbsd['grantResponse'][i]['grantExpireTime'],cbsd['grantResponse'][i]['cbsdId']))
            # sql_device_info_update = "update `dp_device_info` SET sasStage = 'heartbeat' where cbsdID= \'" + cbsd['grantResponse'][i]['cbsdId'] +"\'"
        else:
            errorModule(response['grantResponse'][i])
    #close db connection s

    hbtimer = cbsd['grantResponse'][i]['heartbeatInterval']
    # print(hbtimer)
    conn.dbClose()
    #start spectrum inquiry

def grantRequest():
    #make connection to database
    conn = dbConn("ACS_V1_1")
    #select eveything where sasStage = grant
    sql_select = "select * from dp_device_info WHERE sasStage = \'grant\'"
    cbsd = conn.select(sql_select)
    conn.dbClose()

    if cbsd != ():
        grant = {"grantRequest":[]}
        print("grant request")
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
        logger.log_json(grant,len(cbsd))
        response = contactSAS(grant,"grant")
       
        if response != False:
            grantResponse(response.json())
        # logging.info("RESPONSE FROM grant REQUEST:" + response.json() )
    else:
        pass


def spectrumResponse(response):
    #make connection to domain proxy db
    conn = dbConn("ACS_V1_1")
    #for each resposne in resposne array
    logger.log_json(response,len(response['spectrumInquiryResponse']))
    for i in range(len(response['spectrumInquiryResponse'])):
        
        # logging.info(response['spectrumInquiryResponse'][i]['cbsdId'] + ": Spec Response : " + str(response['spectrumInquiryResponse'][i]))
        
        if response['spectrumInquiryResponse'][i]['response']['responseCode'] == 0:
            # if high frequcy and low frequcy match value(convert to hz) for cbsdId in database then move to next

            #TODO WHAT IF THE AVAIABLE CHANNEL ARRAY IS EMPTY
            low = math.floor(response['spectrumInquiryResponse'][i]['availableChannel'][0]['frequencyRange']['lowFrequency']/1000000)
            high = math.floor(response['spectrumInquiryResponse'][i]['availableChannel'][0]['frequencyRange']['highFrequency']/1000000)

            sql = "SELECT `SN`,`lowFrequency`,`highFrequency` from dp_device_info where cbsdID = \'" + response['spectrumInquiryResponse'][i]['cbsdId'] + "\'"
 
 
            #if the SAS sends back spectrum response with avaible channgel array outsid of the use values set on the cell. Use the values set by the spectrum response
            
            #select values currently used in the database per cbsd
            # cbsd_freq_values = conn.select(sql)
            #  if cbsd_freq_values are outside of the range of low and high(set above) then use value inside the low and high range
            #  cbsdaction(SN,setvalues,now)
            #
 

            sqlUpdate = "update `dp_device_info` SET sasStage = 'grant' where cbsdID= \'" + response['spectrumInquiryResponse'][i]['cbsdId'] +"\'"
            conn.update(sqlUpdate)

    
    #TODO ADD ERROR HANDELING MODULE
    
    conn.dbClose()


def spectrumRequest():

    #ADD form to the web interface to request specific spectrum in MHz. EX: 
    #get EARFCNinUSE for each cbsdID in request (TODO how to change the database to make this query more convienient)
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT cbsdId, EARFCN,lowFrequency,highFrequency FROM dp_device_info where sasStage = \'spectrum\''
    cbsd = conn.select(sql)

    if cbsd != ():
        spec = {"spectrumInquiryRequest":[]}

        for i in range(len(cbsd)):
            # logging.info(f"/////////////////////////SPECTRUM for {cbsd[i]['cbsdId']} \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
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
            # logging.info(spec['spectrumInquiryRequest'][i]['cbsdId']+ ": Spec Request: " + str(spec['spectrumInquiryRequest'][i]))
        logger.log_json(spec,len(cbsd))
        #Send request to SAS server #contact SAS server
        response = contactSAS(spec,"spectrumInquiry")
        # response = {'spectrumInquiryResponse': [{'availableChannel': [{'channelType': 'GAA', 'ruleApplied': 'FCC_PART_96', 'frequencyRange': {'highFrequency': 3585000000, 'lowFrequency': 3565000000 } } ], 'cbsdId': 'FoxconnMock-SASDCE994613163', 'response': {'responseCode': 0} } ] }                                                                                                       
        conn.dbClose()
        #   pass response to spectrum response
        if response != False:
            spectrumResponse(response.json())
        # spectrumResponse(response)
    else:
        conn.dbClose()

def regResponse(response):
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT SN,cbsdId, EARFCN,lowFrequency,highFrequency FROM dp_device_info where sasStage = \'reg\''
    row = conn.select(sql)

    for i in range(len(response['registrationResponse'])):
        logger.log_json(response,(len(response['registrationResponse'])))
        # logging.info(row[i]["SN"] + ": REG Response : " + str(response['registrationResponse'][i]))
        
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
    
def regRequest(cbsds_SN = None):
    
    if cbsds_SN:
        row = query_update(cbsds_SN, 'reg')

    else:
        conn = dbConn("ACS_V1_1")
        sql = 'SELECT * FROM dp_device_info where sasStage = \'reg\''
        row = conn.select(sql)
        conn.dbClose()

    if row != ():
        reg = {"registrationRequest":[]}
        
        for i in range(len(row)):
            # logging.info(f"/////////////////////////REGISTRATION for {row[i]['SN']} \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
            reg['registrationRequest'].append(
                    {
                        "cbsdSerialNumber": str(row[i]["SN"]),
                        "fccId": row[i]["fccID"],
                        "cbsdCategory": str(row[i]["cbsdCategory"]),
                        "userId": str(row[i]["userID"])
                    }
            )
            # logging.info(row[i]["SN"]+ ": Reg Request: " + str(reg['registrationRequest'][i]))

        logger.log_json(reg,len(row))
        response = contactSAS(reg,"registration")
        
        if response != False:
            regResponse(response.json())

        # response = {'registrationResponse': [{'cbsdId': 'FoxconnMock-SASDCE994613163', 'response': {'responseCode': 0}}]}
    else:
        pass
def deregistrationRequest(cbsds_SN = None):

    cbsd_db = query_update(cbsds_SN,'dereg')
    #check for grant ID
    # print(cbsd_db[i]["grantID"])
    # if cbsd_db[i]["grantID"] != None:
    #     print("\n\n is null \n\n")

    #send deregistration
    dereg = {"deregistrationRequest":[]}
    for i in range(len(cbsd_db)):
        #power off RF(How do I know if the CBSD turned off ADMIN_STATE check? do I still need to socket test?)
        cbsdAction(cbsd_db[i]['SN'],"RF_OFF",str(datetime.now()))

        #reliunqish any grants

        #build json request for SAS
        dereg["deregistrationRequest"].append(
            {
                "cbsdId":cbsd_db[i]['cbsdID'],
            }
        )
    logger.log_json(dereg,len(cbsd_db))
    response = contactSAS(dereg,"deregistration")
    deregistrationResposne(response.json())

def deregistrationResposne(response):
    logger.log_json(response,(len(response['deregistrationResponse'])))

    for i in range(len(response['registrationResponse'])):
        if response['registrationResponse'][i]['response']['responseCode'] == 0: 
            pass
            #do nothing
        else:
            errorModule(response['registrationResponse'][i])

def grantRelinquishmentRequest():
    #send relquisment
    #set grant ID to NULL
    pass
def grantRelinquishmentResponse():
    pass


def query_update(cbsds_SN_list, sasStage):
    conn = dbConn("ACS_V1_1")
    sql_select = "select * from dp_device_info where `SN` in "+ str(cbsds_SN_list) +";"
    rows = conn.select(sql_select)
    sql_update = "UPDATE dp_device_info SET sasStage = %s WHERE SN in" + str(cbsds_SN_list) +";"
    conn.update(sql_update,sasStage)
    conn.dbClose()
    return rows

def errorModule(response):
    #TODO check for operational params
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
def registration():
    while True:
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
    # SNlist = {"SN1":"DCE994613163","SN2":"abc123"}
    # SN_json_dict = json.loads(SNlist)
    # regRequest(("DCE994613163","abc123"))
    response = {'deregistrationRequest': [{'cbsdId': 'FoxconnMock-SASabc123'}, {'cbsdId': 'FoxconnMock-SASDCE994613163'}]}
    deregistrationResposne(response)
start()
# test()

# try:
#     a_socket.connect(("192.168.4.5", 10500))
#     print("connected")
# except:
#     print("Connection failed")
#     #     conn.dbClose()

# while True:


# def some_test(cbsd):
#     with socket.socket() as s:
#         try:
#             s.connect((cbsd, 10500))
#             print(f"connected to ip: {cbsd}")
#         except Exception as e:
#             print(f"Connection failed reason: {e}")
#         time.sleep(10)
#         s.close()
#         print("finished")

# cbsds = ["192.168.4.5", "192.168.4.9"]
# for cbsd in cbsds:
#     print(cbsd)
#     try:
#         #comma for tuple
#         thread = threading.Thread(target=some_test, args=(cbsd,))
#         thread.start()
#     except Exception as e:
#         print(f"Connection failed reason: {e}")
    

            
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

