import requests
import sys
from lib.db.dbConn import dbConn
from test import app
import json
import flask
from flask import request
import math
import time
from datetime import datetime
import logging

hbtimer = 0

def contactSAS(request,method):
    # Function to contact the SAS server
    # request - json array to pass to SAS
    # method - which method SAS you would like to contact registration, spectrum, grant, heartbeat 

    return requests.post(app.config['SAS']+method, 
    cert=('certs/client.cert','certs/client.key'),
    verify=('certs/ca.cert'),
    json=request)

def EARFCNtoMHZ(cbsd):
    # Function to convert frequency from EARFCN  to MHz 3660 - 3700
    # mhz plus 6 zeros
    # L_frq = 0
    # H_frq = 0
    # conn = dbConn("ACS_V1_1")

    for i in range(len(cbsd)):
        if int(cbsd[i]['EARFCN']) > 56739 or int(cbsd[i]['EARFCN']) < 55240:
            return "SPECTRUM IS OUTSIDE OF BOUNDS"
        else:
            F = math.ceil(3550 + (0.1 * (int(cbsd[i]['EARFCN']) - 55240)))

            #web gui that asks for high and low ranges?
            print("EARFCN: " + str(cbsd[i]['EARFCN']))
            if F <= 3680:
                L_frq = F
                H_frq = L_frq + 20
            else:
                H_frq = F 
                L_frq = H_frq - 20

            print(L_frq,H_frq)

            # SWITCH CASE FOR LOW and HIGH frequency
            # if F >= 3550 and F <= 3570:
            #     L_frq = 3550
            #     H_frq = 3570
            # elif F > 3570 and F <= 3590:
            #     L_frq = 3570
            #     H_frq = 3590
            # elif F > 3590 and F <= 3610:
            #     L_frq = 3590
            #     H_frq = 3610
            # elif F > 3610 and F <= 3630:
            #     L_frq = 3610
            #     H_frq = 3630
            # elif F > 3630 and F <= 3650:
            #     L_frq = 3630
            #     H_frq = 3650
            # elif F > 3650 and F <= 3670:
            #     L_frq = 3650
            #     H_frq = 3670
            # else:

            # logging.info(cbsd)
            # logging.info(str(L_frq) + " " + str(H_frq))

        #Upload MHz to dp_device_info table
        
    #     sql = "UPDATE `dp_device_info` SET lowFrequency=\'"+str(L_frq)+"\', highFrequency=\'"+str(H_frq)+"\' WHERE cbsdID = \'"+cbsd[i]['cbsdID']+"\'"
    #     try:
    #         # print(sql)
    #         conn.cursor.execute(sql)
    #     except Exception as e:
    #         logging.error(e)

    # conn.dbClose()

def heartbeatResponse(cbsd):
    # print(cbsd)


    #Make connection to ACS_V1_1 database
    conn = dbConn("ACS_V1_1")
    for i in range(len(cbsd['heartbeatResponse'])):
        #if error code = 0 then process handle reply for cbsd
        # print(cbsd['heartbeatResponse'][i])
        if cbsd['heartbeatResponse'][i]['response']['responseCode'] == 0: 
        #TODO what if no reply... lost in the internet
        #TODO check if reply is recieved from all cbsds
        #TODO WHAT IF NEW OPERATIONAL PARAMS
        #TODO WHAT IF MEAS REPORT

            sql_get_op = "SELECT operationalState FROM dp_heartbeat WHERE cbsdID = \'"+cbsd['heartbeatResponse'][i]['cbsdId']+"\'"
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
                sql_action = "INSERT INTO apt_action_queue (SN,Action,ScheduleTime) values(\'"+sn['SN']+"\','RF_ON',\'"+str(datetime.now())+"\')"
                conn.cursor.execute(sql_action)
            # print(sql_action)


        #if operational state  = gratned turn rf on

    #else handle error

    #close database
    conn.dbClose()

def heartbeatRequest(cbsd):
    heartbeat = {"heartbeatRequest":[]}

    for i in range(len(cbsd)):
        heartbeat['heartbeatRequest'].append(
                {
                    "cbsdId":cbsd[i]['cbsdID'],
                    "grantId":cbsd[i]['grantID'],
                    "operationState":cbsd[i]['operationalState']
                }
            )


    logging.info("REQUEST FROM heartbeat: " + str(heartbeat))
    response = contactSAS(heartbeat,"heartbeat")
    logging.info("RESPONSE FROM heartbeat: " + str(response))
    heartbeatResponse(response.json())



def grantResponse(cbsd):
    #Make connection to ACS_V1_1 database
    conn = dbConn("ACS_V1_1")
    for i in range(len(cbsd['grantResponse'])):
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



    logging.info("REQUEST FROM GRANT: " + str(grant))
    # print(grant)
    response = contactSAS(grant,"grant")
    
    
    grantResponse(response.json())
    logging.info("RESPONSE FROM grant REQUEST:" + response.json())


def spectrumResponse(response):
    #make connection to domain proxy db
    conn = dbConn("ACS_V1_1")
    #for each resposne in resposne array
    for i in range(len(response['spectrumInquiryResponse'])):
        if response['spectrumInquiryResponse'][i]['response']['responseCode'] == 0:
            # if high frequcy and low frequcy match value(convert to hz) for cbsdId in database then move to next
            low = math.floor(response['spectrumInquiryResponse'][i]['availableChannel'][0]['frequencyRange']['lowFrequency']/1000000)
            high = math.floor(response['spectrumInquiryResponse'][i]['availableChannel'][0]['frequencyRange']['highFrequency']/1000000)

            sql = "SELECT `lowFrequency`,`highFrequency` from dp_device_info where cbsdID = \'" + response['spectrumInquiryResponse'][i]['cbsdId'] + "\'"
            try:
                conn.cursor.execute(sql)
                freq = conn.cursor.fetchall()
            except Exception as e:
                print(e)

            #if frequncy on cell is within the range of the spectrum request move to next cbsd
            if freq[0]['lowFrequency'] < low or freq[0]['highFrequency'] > high:
                print("FREQUENCY ERROR!!!")
                #TODO if they do not match update with the range provided by SAS or just widen search
            else:
                sql = "update `dp_device_info` SET sasStage = 'grant' where cbsdID= \'" + response['spectrumInquiryResponse'][i]['cbsdId'] +"\'"
                conn.cursor.execute(sql)

    #TODO WHAT IF THE AVAIABLE CHANNEL ARRAY IS EMPTY
    #TODO ADD ERROR HANDELING MODULE
    
    conn.dbClose()


def spectrumRequest(cbsd):

    #ADD form to the web interface to request specific spectrum in MHz. EX: 
    #get EARFCNinUSE for each cbsdID in request (TODO how to change the database to make this query more convienient)
    # conn = dbConn("ACS_V1_1")
    # sql = 'SELECT EARFCNinUSE FROM apt_cpe_list WHERE SN = \'DCE994613163\''
    # conn.cursor.execute(sql)
    # row = conn.cursor.fetchone()
    # conn.dbClose()
    spec = {"spectrumInquiryRequest":[]}
    # print(row['EARFCNinUSE'])
    # print(db[0]['EARFCN'])
    for i in range(len(cbsd)):
        #Convert from EARFCN to MHz accounting for bandwidth of 20MHz for each cbsdID in request
        #build json request for SAS for each row in request
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
    
    logging.info("REQUEST FOR SPECTRUM INQUIRY: " + str(spec) )
    # #Send request to SAS server #contact SAS server
    response = contactSAS(spec,"spectrumInquiry")
    # # #pass response to spectrum response
    logging.info("RESPONSE FOR SPECTRUM INQUIRY:",response.json())
    spectrumResponse(response.json())

def regResponse(response,row):
    #Make connection to ACS_V1_1 database
    conn = dbConn("ACS_V1_1")
    for i in range(len(response['registrationResponse'])):
        #Check if responseCode is > 0 
        if response['registrationResponse'][i]['response']['responseCode'] == 0: 
            #TODO Check for measurement Report

            #Update cbsdID, SAS_STAGE in device info table
            sql = "UPDATE `dp_device_info` SET cbsdID=\""+response['registrationResponse'][i]['cbsdId']+"\",sasStage=\"spectrum\" WHERE SN=\'"+row[i]["SN"]+"\'"
            print(sql)
            try:
                # print(sql)
                conn.cursor.execute(sql)
            except Exception as e:
                print(e)
        else:
            errorModule(response['registrationResponse'][i])
    #close db connection s
    conn.dbClose()
    #start spectrum inquiry


def regRequest(row):
    #create reg request
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
    # print("REQUEST FROM REG",reg)

    logging.info("REQUEST FROM REG:" + str(reg))
 
    response = contactSAS(reg,"registration")
    
    logging.info("RESPONSE FROM REG REQUEST",response.json())

    regResponse(response.json(),row)
    


def errorModule(response):
    #add some sort of logging mechanism something like ECCLogger
    print("!!!Error!!!")
    print(response)
    print("!!!Error!!!")


if __name__ == "__main__":
    # COLLECT ALL DEVICES LOOKING TO BE REGISTERED

    # logging.basicConfig(filename='/tmp/dp.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    # logging.warning('This will get logged to a file')
    logging.basicConfig(filename="/tmp/dp.log",format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')

    # # EARFCNtoMHZ([{'EARFCN':55240},{'EARFCN':55990},{'EARFCN':56739}])
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT * FROM dp_device_info where sasStage = \'\''
    conn.cursor.execute(sql)
    reg = conn.cursor.fetchall()
    conn.dbClose()
    print("reg", flush=True)

    try:
        regRequest(reg)
        EARFCNtoMHZ(reg)
    except Exception as e:
        print(e)

    conn = dbConn("ACS_V1_1")
    sql = 'SELECT cbsdId, EARFCN,lowFrequency,highFrequency FROM dp_device_info where sasStage = \'spectrum\''
    conn.cursor.execute(sql)
    spec = conn.cursor.fetchall()
    conn.dbClose()

    print("spec")
    try:
        spectrumRequest(spec)
    except Exception as e:
        print(e)

    # spec = {'spectrumInquiryResponse': [{'availableChannel': [{'channelType': 'GAA', 'ruleApplied': 'FCC_PART_96', 'frequencyRange': {'highFrequency': 3570000000, 'lowFrequency': 3550000000}}], 'cbsdId': 'abc123Mock-SAS1111', 'response': {'responseCode': 0}}, {'availableChannel': [{'channelType': 'GAA', 'ruleApplied': 'FCC_PART_96', 'frequencyRange': {'highFrequency': 3700000000, 'lowFrequency': 3670000000}}], 'cbsdId': 'xyz123Mock-SAS4444', 'response': {'responseCode': 0}}]}

    # try:
    #     spectrumResponse(spec)
    # except Exception as e:
    #     print(e)

    conn = dbConn("ACS_V1_1")
    sql = 'SELECT * FROM dp_device_info where sasStage = \'grant\''
    conn.cursor.execute(sql)
    grant = conn.cursor.fetchall()
    conn.dbClose()

    print("grant")
    #TODO FINISH grantRequest
    try:
        grantRequest(grant)
    except Exception as e:
        print(e)

    #TODO if error break
    #TODO LOOP AT 80% OF heartbeat TIMER
    while True:
        # print("hb")
        conn = dbConn("ACS_V1_1")
        sql = 'SELECT * FROM dp_heartbeat'
        conn.cursor.execute(sql)
        hb = conn.cursor.fetchall()
        conn.dbClose()
        # print(hb)

        try:
            heartbeatRequest(hb)
        except Exception as e:
            print(e)
        # 80% of hbtimer
        time.sleep(45)


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

app.run(port = app.config["PORT"])

