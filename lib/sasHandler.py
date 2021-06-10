from config.default import SAS
import math
import logging
import requests
import time
import lib.consts as consts
from lib.log import dpLogger
from lib.dbConn import dbConn
from lib import error as e
from datetime import datetime, timedelta
from test import app


def Handle_Request(cbsd_list,typeOfCalling):
    '''
    handles all requests send to SAS
    '''
    requestMessageType = str(typeOfCalling +"Request")

    req = {requestMessageType:[]}

    for cbsd in cbsd_list:

        if typeOfCalling == consts.REG:
            req[requestMessageType].append(
                {
                    "cbsdSerialNumber": cbsd["SN"],
                    "fccId": cbsd["fccID"],
                    "cbsdCategory": cbsd["cbsdCategory"],
                    "userId": cbsd["userID"]
                }
            )
        
        elif typeOfCalling == consts.SPECTRUM:
            
            #calculate MHz and MaxEirp
            FreqDict = EARFCNtoMHZ(cbsd['SN'])

            req[requestMessageType].append(
                {
                    "cbsdId":cbsd['cbsdID'],
                    "inquiredSpectrum":[
                        {
                            "highFrequency":FreqDict['highFreq'] * 1000000,
                            "lowFrequency":FreqDict['lowFreq']  * 1000000
                        }
                    ]
                }
            )
        
        elif typeOfCalling == consts.GRANT:
            
            req[requestMessageType].append(
                    { 
                        "cbsdId":cbsd['cbsdID'],
                        "operationParam":{
                            # grab antennaGain from web interface
                            "maxEirp":cbsd['maxEIRP'],
                            "operationFrequencyRange":{
                                "lowFrequency":cbsd['lowFrequency'] * 1000000,
                                "highFrequency":cbsd['highFrequency'] * 1000000
                            }
                        }
                    }
                )
        elif typeOfCalling == consts.HEART:

            grantRenew = False
           
            
            logging.info(f"GRANT EXPIRE TIME: {cbsd['grantExpireTime']}")
            
            #check if grant is expired
            if expired(cbsd['grantExpireTime'],True):
                grantRenew = True 
            
            #check if we are transmiting with an expired heartbeat
            if cbsd['operationalState'] == 'AUTHORIZED':
                #in the case of no reply from SAS continue to check transmit expire time and switch opState to granted and turn off RF if we exceed transmit time
                opState = getOpState(cbsd)
            else:
                opState = 'GRANTED'
            
            req[requestMessageType].append(
                    {
                        "cbsdId":cbsd['cbsdID'],
                        "grantId":cbsd['grantID'],
                        "operationState":opState,
                        "grantRenew":grantRenew
                    }
                )
        elif typeOfCalling == consts.DEREG:
            
            #if adminstate is on turn off.

            #get parameter value
            # cbsdAction(cbsd['SN'],"RF_OFF",str(datetime.now()))
            if cbsd['AdminState'] == 1:
                setParameterValue(cbsd['SN'],consts.ADMIN_STATE,'boolean','false')
            
            #if grantID != NULL
            # call grant relinquish
            req[requestMessageType].append(
                    {
                        "cbsdId":cbsd['cbsdID'],
                    }
                )

        elif typeOfCalling == consts.REL:

            #Set small cell admin state to false
            if cbsd['AdminState'] == 1:
                setParameterValue(cbsd['SN'],consts.ADMIN_STATE,'boolean','false')
            
            
            req[requestMessageType].append(
                {
                    "cbsdId":cbsd['cbsdID'],
                    "grantId":cbsd['grantID']
                }
            )
            #set grant IDs to NULL
            conn = dbConn("ACS_V1_1")
            update_grantID = "UPDATE dp_device_info SET grantID = NULL, SET operationalState = NULL, SET grantExpireTime = NULL, SET transmitExpireTime = NULL WHERE SN = %s "
            conn.update(update_grantID,cbsd['SN'])
            conn.dbClose()

    dpLogger.log_json(req,len(cbsd_list))
    SASresponse = contactSAS(req,typeOfCalling)

    if SASresponse != False:
        Handle_Response(cbsd_list,SASresponse.json(),typeOfCalling)

    # if SASresponse != False:
    #     Handle_Response(cbsd_list,SASresponse,typeOfCalling)

def Handle_Response(cbsd_list,response,typeOfCalling):
    #HTTP address that is in place e.g.(reg,spectrum,grant heartbeat)
    resposneMessageType = str(typeOfCalling +"Response")
    
    # select all cbsd that are in current step for typeOfCalling
    # conn = dbConn("ACS_V1_1")
    # sql = 'SELECT * FROM dp_device_info where sasStage = %s' 
    # cbsd_list = conn.select(sql,typeOfCalling)
    # conn.dbClose()

    #init dict to pass to error module
    errorDict = {}
    errorList = []
    
    dpLogger.log_json(response,(len(response[resposneMessageType])))
    
    for i in range(len(response[resposneMessageType])):

        #check for errors in response
        if response[resposneMessageType][i]['response']['responseCode'] != 0:

            errorCode = response[resposneMessageType][i]['response']['responseCode']

            #if transmit expire in response
            if 'transmitExpireTime' in response[resposneMessageType][i]:
                conn = dbConn("ACS_V1_1")
                #update transmit expire in the database for cbsd_list[i]
                conn.update("UPDATE dp_device_info SET transmitExpireTime = %s WHERE SN = %s",(response[resposneMessageType][i]['transmitExpireTime'],cbsd_list[i]['SN']))
                #get new data from databbase for cbsd
                cbsd = conn.select("SELECT * from dp_device_info WHERE SN = %s",cbsd_list[i]['SN'])
                #pass to addErrordict
                addErrorDict(errorCode,errorDict,cbsd[0])
            else:
                addErrorDict(errorCode,errorDict,cbsd_list[i])

            errorList.append(cbsd_list[i]['SN'])
            
            # errorDict[cbsd_list[i]['SN']] = response[resposneMessageType][i]

        elif typeOfCalling == consts.REG:

            conn = dbConn("ACS_V1_1")
            sqlUpdate = "UPDATE `dp_device_info` SET cbsdID=\""+response['registrationResponse'][i]['cbsdId']+"\",sasStage=\"spectrumInquiry\" WHERE SN=\'"+cbsd_list[i]["SN"]+"\'"
            conn.update(sqlUpdate)

            #nextCalling = conts.SPECTRUM

        elif typeOfCalling == consts.SPECTRUM:
            conn = dbConn("ACS_V1_1")
            # if high frequcy and low frequcy match value(convert to hz) for cbsdId in database then move to next


            #check maxEirp if higher change

            # print(len(response['spectrumInquiryResponse'][i]['availableChannel']))

            # for channel in response['spectrumInquiryResponse'][i]['availableChannel']:
            #      if channel['channelType'] == 'GAA':
            #         if channel['maxEirp'] <= cbsd_list[i]['maxEIRP']:
            #             print("over")
            #         print(channel['frequencyRange']['lowFrequency'],channel['frequencyRange']['highFrequency'])
                       
               
            #TODO WHAT IF THE AVAIABLE CHANNEL ARRAY IS EMPTY
            low = math.floor(response['spectrumInquiryResponse'][i]['availableChannel'][0]['frequencyRange']['lowFrequency']/1000000)
            high = math.floor(response['spectrumInquiryResponse'][i]['availableChannel'][0]['frequencyRange']['highFrequency']/1000000)

            sql = "SELECT `SN`,`lowFrequency`,`highFrequency` from dp_device_info where cbsdID = \'" + response['spectrumInquiryResponse'][i]['cbsdId'] + "\'"

            #if the SAS sends back spectrum response with avaible channgel array outsid of the use values set on the cell. Use the values set by the spectrum response
            
            #select values currently used in the database per response
            # cbsd_freq_values = conn.select(sql)
            #  if cbsd_freq_values are outside of the range of low and high(set above) then use value inside the low and high range
            #  cbsdaction(SN,setvalues,now)
            #
            sqlUpdate = "update `dp_device_info` SET sasStage = 'grant' where cbsdID= \'" + response['spectrumInquiryResponse'][i]['cbsdId'] +"\'"
            conn.update(sqlUpdate)

            #nextCalling = consts.GRANT

        elif typeOfCalling == consts.GRANT:
            #TODO Check for measurement Report
            
            conn = dbConn("ACS_V1_1")
            sql_update = "UPDATE `dp_device_info` SET `grantID` = %s , `grantExpireTime` = %s, `operationalState` = \'GRANTED\', `sasStage` = \'heartbeat\' WHERE `cbsdID` = %s"
            conn.update(sql_update,(response['grantResponse'][i]['grantId'],response['grantResponse'][i]['grantExpireTime'],response['grantResponse'][i]['cbsdId']))
            conn.dbClose()

            #nextCalling = consts.HEART

        elif typeOfCalling == consts.HEART: 
            #TODO what if no reply... lost in the internet
            #TODO check if reply is recieved from all cbsds
            #TODO WHAT IF MEAS REPORT
            #TODO

            conn = dbConn("ACS_V1_1")
            # print(f"resposne transmist expire time {response['heartbeatResponse'][i]['transmitExpireTime']}")
            
            #update operational state to granted/ what if operational state is already authorized
            if not expired(response['heartbeatResponse'][i]['transmitExpireTime']):
                update_operational_state = "UPDATE dp_device_info SET operationalState = CASE WHEN operationalState = 'GRANTED' THEN 'AUTHORIZED' ELSE 'AUTHORIZED' END WHERE cbsdID = \'" + response['heartbeatResponse'][i]['cbsdId'] + "\'"
                conn.update(update_operational_state)
            
            #update transmist expire time
            update_transmit_time = "UPDATE dp_device_info SET transmitExpireTime = \'" + response['heartbeatResponse'][i]['transmitExpireTime'] + "\' where cbsdID = \'" + response['heartbeatResponse'][i]['cbsdId'] + "\'"
            conn.update(update_transmit_time)
            conn.dbClose()

            #collect SN from dp_device_info where cbsdId = $cbsdid
            if cbsd_list[i]['operationalState'] == 'GRANTED':
                print("!!!!!!!!!!!!!!!!GRATNED!!!!!!!!!!!!!!!!!!!!!!!!")
                # turn on RF in cell
                # cbsdAction(cbsd_list[i]['SN'],"RF_ON",str(datetime.now()))
                if cbsd_list[i]['AdminState'] != 1:
                    setParameterValue(cbsd_list[i]['SN'],consts.ADMIN_STATE,'boolean','true')

            #if response has new grantTime update databas
            if 'grantExpireTime' in response['heartbeatResponse'][i]:
                updateGrantTime(response['heartbeatResponse'][i]['grantExpireTime'],cbsd_list[i]['SN'])

        elif typeOfCalling == consts.DEREG:
            #update sasStage
            conn = dbConn("ACS_V1_1") 
            conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.DEREG,cbsd_list[i]['SN']))
            conn.dbClose()


        elif typeOfCalling == consts.REL:
            #update sasStage
            conn = dbConn("ACS_V1_1")
            conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.REL,cbsd_list[i]['SN']))
            conn.dbClose()


    if bool(errorDict):
        e.errorModule(errorDict,typeOfCalling)
        cbsd_list[:] = [cbsd for cbsd in cbsd_list if not hasError(cbsd,errorList)]

    if bool(cbsd_list):
        nextCalling = getNextCalling(typeOfCalling)
        #should rather make cbsd a class
        #update cbsd list properties
        
        if (nextCalling != False):
            conn = dbConn("ACS_V1_1")
            updated_cbsd_list = conn.select("SELECT * FROM dp_device_info WHERE sasStage = %s",nextCalling)
            Handle_Request(updated_cbsd_list,nextCalling)



def updateGrantTime(grantExpireTime,SN):
    conn = dbConn("ACS_V1_1")
    conn.update("UPDATE dp_device_info SET grantExpireTime = %s WHERE SN = %s",(grantExpireTime,SN))
    conn.dbClose()


def contactSAS(request,method):
    # Function to contact the SAS server
    # request - json array to pass to SAS
    # method - which method SAS you would like to contact registration, spectrum, grant, heartbeat 
    # logger.info(f"{app.config['SAS']}  {method}")

    try:
        return requests.post(app.config['SAS']+method, 
        cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
        verify=('googleCerts/ca.cert'),
        json=request)

        # timeout=5
        
    except Exception as e:
        print(f"your connection has failed: {e}")
        return False
    # return consts.FS1
def getOpState(cbsd):

    if expired(cbsd['transmitExpireTime'] ):
        opState = 'GRANTED'
        conn = dbConn("ACS_V1_1")
        conn.update("UPDATE dp_device_info SET operationalState = 'GRANTED' WHERE SN = %s",cbsd['SN'])
        conn.dbClose()
        #turn RF Off
        # cbsdAction(cbsd['SN'],"RF_OFF",str(datetime.now()))
        setParameterValue(cbsd['SN'],consts.ADMIN_STATE,'boolean','false')
    else:
        opState = 'AUTHORIZED'

    return opState

def cbsdAction(cbsdSN,action,time):

    #check note field for EXEC
    logging.critical("Triggering CBSD action")
    conn = dbConn("ACS_V1_1")
    sql_action = "INSERT INTO apt_action_queue (SN,Action,ScheduleTime) values(\'"+cbsdSN+"\',\'"+action+"\',\'"+time+"\')"
    logging.critical(cbsdSN + " : SQL cmd " + sql_action)
    conn.update(sql_action)
    conn.dbClose()

def MHZtoEARFCN(cbsd):
    

    #take low freq in MHz and 10(to get the middle freq)
    MHz = int(cbsd['lowFrequency']) + 10

    #then convert to EARFCN
    EARFCN = math.ceil(((MHz - 3550)/0.1) + 55240)

    return EARFCN

def EARFCNtoMHZ(cbsd_SN):
    # Function to convert frequency from EARFCN  to MHz 3660 - 3700
    # mhz plus 6 zeros
    freqDict = {}
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT * FROM dp_device_info where SN = %s'
    cbsd = conn.select(sql,cbsd_SN)

    
    logging.info("////////////////////////////////EARFCN CONVERTION "+ cbsd[0]['SN']+"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
    print("EARFCN: " + str(cbsd[0]['EARFCN']))
    if int(cbsd[0]['EARFCN']) > 56739 or int(cbsd[0]['EARFCN']) < 55240:
        logging.info("SPECTRUM IS OUTSIDE OF BOUNDS")
        L_frq = 0
        H_frq = 0
    elif cbsd[0]['EARFCN'] == 55240:
        L_frq = 3550
        H_frq = 3570
    elif cbsd[0]['EARFCN'] == 56739:
        L_frq = 3680
        H_frq = 3700
    else:
        F = math.ceil(3550 + (0.1 * (int(cbsd[0]['EARFCN']) - 55240)))
        L_frq = F - 10
        H_frq = F + 10

    sql = "UPDATE `dp_device_info` SET lowFrequency= %s, highFrequency=%s, maxEIRP= %s WHERE SN = %s"
    conn.update(sql,(str(L_frq),str(H_frq),int(cbsd[0]['TxPower'] + cbsd[0]['antennaGain']), str(cbsd[0]['SN'])))        
    conn.dbClose()

    freqDict['lowFreq'] = L_frq
    freqDict['highFreq'] = H_frq
    return freqDict

def hasError(cbsd,errorList):
    if cbsd['SN'] in errorList:
        return True
    else:
        return False

def getNextCalling(typeOfCalling):
    if typeOfCalling == consts.REG:
        return consts.SPECTRUM
    if typeOfCalling == consts.SPECTRUM:
        return consts.GRANT
    if typeOfCalling == consts.GRANT:
        return consts.HEART
    if typeOfCalling == consts.HEART:
        return False
    if typeOfCalling == consts.REL:
        return False
    if typeOfCalling == consts.DEREG:
        return False

def setParameterValue(cbsd_SN,data_model_path,setValueType,setValue,index = 1):
    #purge last action
    conn = dbConn("ACS_V1_1")
    conn.update('DELETE FROM fems_spv WHERE SN = %s',cbsd_SN)

    #update Adminstate in DB
    if data_model_path == consts.ADMIN_STATE and setValue == 'false':
        logging.info("Turn RF OFF for %s",cbsd_SN)
        conn.update("UPDATE dp_device_info SET AdminState = 0 WHERE SN = %s",cbsd_SN)

    if data_model_path == consts.ADMIN_STATE and setValue == 'true':
        logging.info("Turn RF ON for %s",cbsd_SN)
        conn.update("UPDATE dp_device_info SET AdminState = 1 WHERE SN = %s",cbsd_SN)

    #insert SN, data_model_path and value into FeMS_spv
    conn.update('INSERT INTO fems_spv(`SN`, `spv_index`,`dbpath`, `setValueType`, `setValue`) VALUES(%s,%s,%s,%s,%s)',(cbsd_SN,index,data_model_path,setValueType,setValue))
    conn.dbClose()
    #call cbsdAction with action as 'Set Parameter Value'
    cbsdAction(cbsd_SN,'Set Parameter Value',str(datetime.now()))


def setParameterValues(pDict,cbsd):
    p = pDict[cbsd['SN']]
    #purge last action(s)
    conn = dbConn("ACS_V1_1")
    conn.update('DELETE FROM fems_spv WHERE SN = %s',cbsd)['SN']

    for i in range(len(p)):
        
        #update Adminstate in DB
        if p[i]['data_path'] == consts.ADMIN_STATE and p[i]['data_value'] == 'false':
            logging.info("Turn RF OFF for %s",cbsd['SN'])
            conn.update("UPDATE dp_device_info SET AdminState = 0 WHERE SN = %s",cbsd['SN'])

        if p[i]['data_path'] == consts.ADMIN_STATE and p[i]['data_value'] == 'true':
            logging.info("Turn RF ON for %s",cbsd['SN'])
            conn.update("UPDATE dp_device_info SET AdminState = 1 WHERE SN = %s",cbsd['SN'])

    
        conn.update('INSERT INTO fems_spv(`SN`, `spv_index`,`dbpath`, `setValueType`, `setValue`) VALUES(%s,%s,%s,%s,%s)',(cbsd['SN'],i,p[i]['data_path'],p[i]['data_type'],p[i]['data_value']))
    
    conn.dbClose()
    #call cbsdAction with action as 'Set Parameter Value'

    with socket.socket() as s:
        try:
            s.connect((cbsd['IPAddress'], 10500))
            print(f"connected to ip: 192.168.4.17")
            cbsdAction(cbsd['SN'],'Set Parameter Value',str(datetime.now()))
        except Exception as e:
            print(f"Connection failed reason: {e}")
        s.close()
        print("finished")
    


    

def getParameterValue():
    pass
    # check if action is already being executed
    # sqlQueryStr = "SELECT `Note` FROM `apt_action_queue` WHERE `Action`='".$In_Action."' AND `SN`='".$In_SN."'";
    # $sqlQueryResult = mysql_query($sqlQueryStr);
    # if(mysql_num_rows($sqlQueryResult) != 0)
    # {
    #     $note = mysql_result($sqlQueryResult, 0);
    #     if (!empty($note) && ($note == 'EXEC')) /* block replacement if action is executing */
    #     {
    #         echo '<script language="javascript">alert("Previous GPV is running, please retry later");top.location.href=\'deviceList.php\';</script>';
    #         exit();                
    #     }
    # }

    #if no action purge last action

def expired(transmitExpireTime, grantRenew = False):
    #convert transmitExpireTime string to datetime
    if transmitExpireTime == None:
        return False
    
    expireTime = datetime.strptime(transmitExpireTime,"%Y-%m-%dT%H:%M:%SZ")

    if grantRenew:
        expireTime = expireTime - timedelta(seconds=280)
   
    if datetime.utcnow() > expireTime:
        return True
    else: 
        return False

def addErrorDict(errorCode,errorDict,cbsd):
    #if key in dict
    if errorCode in errorDict:
        #append list
        errorDict[errorCode].append(cbsd)
    else:
        #create key and list
        errorDict[errorCode] = []
        errorDict[errorCode].append(cbsd)
        # append list