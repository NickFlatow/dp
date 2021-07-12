from config.default import SAS
import math
import json
import logging
import requests
import socket
import time
import lib.consts as consts
from lib.log import dpLogger
from lib.dbConn import dbConn
from lib import error as err
from datetime import datetime, timedelta
from requests.auth import HTTPDigestAuth
from test import app

def Handle_Request(cbsd_list,typeOfCalling):
    '''
    handles all requests sent to the SAS
    '''
    if typeOfCalling == consts.HEART or typeOfCalling == consts.SUB_HEART:
        requestMessageType = str(consts.HEART + "Request")
    else:
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
            
            req[requestMessageType].append(
                {
                    "cbsdId":cbsd['cbsdID'],
                    "inquiredSpectrum":[
                        {
                            "highFrequency":consts.HIGH_FREQUENCY,
                            "lowFrequency":consts.LOW_FREQUENCY
                        }
                    ]
                }
            )
        
        elif typeOfCalling == consts.GRANT:
            
            # req[requestMessageType].append(
            #         { 
            #             "cbsdId":cbsd['cbsdID'],
            #             "operationParam":{
            #                 "maxEirp":cbsd['maxEIRP'],
            #                 "operationFrequencyRange":{
            #                     "lowFrequency":cbsd['lowFrequency'] * 1000000,
            #                     "highFrequency":cbsd['highFrequency'] * 1000000
            #                 }
            #             }
            #         }
            #     )

            req[requestMessageType].append(
                { 
                    "cbsdId":cbsd['cbsdID'],
                    "operationParam":{
                        "maxEirp":cbsd['maxEIRP'],
                        "operationFrequencyRange":{
                            "lowFrequency":3660 * 1000000,
                            "highFrequency":3680 * 1000000
                        }
                    }
                }
            )
        elif typeOfCalling == consts.HEART:
            req[requestMessageType].append(
                {
                    "cbsdId":cbsd['cbsdID'],
                    "grantId":cbsd['grantID'],
                    "operationState":'GRANTED',
                    "grantRenew":False
                }
            )


        elif typeOfCalling == consts.SUB_HEART:

            grantRenew = False
           
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
                setList  = [consts.ADMIN_POWER_OFF]
                #power off ASAP
                setParameterValues(setList,cbsd)
            
            #if grantID != NULL
            # call grant relinquish
            req[requestMessageType].append(
                    {
                        "cbsdId":cbsd['cbsdID'],
                    }
                )
            conn = dbConn("ACS_V1_1")
            update_grantID = "UPDATE dp_device_info SET operationalState = NULL, grantExpireTime = NULL, transmitExpireTime = NULL, sasStage = %s WHERE SN = %s"
            conn.update(update_grantID,(consts.DEREG,cbsd['SN']))
            conn.dbClose()

        elif typeOfCalling == consts.REL:

            #Set small cell admin state to false
            if cbsd['AdminState'] == 1:
                setList  = [consts.ADMIN_POWER_OFF]
                #power off ASAP
                setParameterValues(setList,cbsd)
            
            
            req[requestMessageType].append(
                {
                    "cbsdId":cbsd['cbsdID'],
                    "grantId":cbsd['grantID']
                }
            )
            #set grant IDs to NULL and sasStage to relinquish
            conn = dbConn("ACS_V1_1")
            update_grantID = "UPDATE dp_device_info SET grantID = NULL, operationalState = NULL, grantExpireTime = NULL, transmitExpireTime = NULL, sasStage = %s WHERE SN = %s"
            conn.update(update_grantID,(consts.REL,cbsd['SN']))
            conn.dbClose()

    dpLogger.log_json(req,len(cbsd_list))
    SASresponse = contactSAS(req,typeOfCalling)
    # SASresponse = True

    if SASresponse != False:
        conn = dbConn("ACS_V1_1")
        updated_cbsd_list = conn.select("SELECT * FROM dp_device_info WHERE sasStage = %s",typeOfCalling)
        conn.dbClose()
        # Handle_Response(updated_cbsd_list,consts.GR,typeOfCalling)
        Handle_Response(updated_cbsd_list,SASresponse.json(),typeOfCalling)

    #if we get no reply from sas and we are in the initial heartbeat stage switch to subsequent heartbeat and keep trying
    elif SASresponse == False and typeOfCalling == consts.HEART:
        conn = dbConn(consts.DB)
        for cbsd in cbsd_list:
            cbsd['sasStage'] = consts.SUB_HEART
            conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.SUB_HEART,cbsd['SN']))
        conn.dbClose()

def Handle_Response(cbsd_list,response,typeOfCalling):
    #HTTP address that is in place e.g.(reg,spectrum,grant heartbeat)
    if typeOfCalling == consts.HEART or typeOfCalling == consts.SUB_HEART:
        resposneMessageType = str(consts.HEART + "Response")
    else:
        resposneMessageType = str(typeOfCalling +"Response")
    

    #init dict to pass to error module
    errorDict = {}
    errorList = []
    
    dpLogger.log_json(response,(len(response[resposneMessageType])))
    
    for i in range(len(response[resposneMessageType])):


        #check for errors in response
        if response[resposneMessageType][i]['response']['responseCode'] != 0:

            errorCode = response[resposneMessageType][i]['response']['responseCode']

            if 'transmitExpireTime' in response[resposneMessageType][i] and cbsd_list[i]['AdminState'] == 1:
                if expired(response['heartbeatResponse'][i]['transmitExpireTime']):
                    setList  = [consts.ADMIN_POWER_OFF]
                    #power off ASAP
                    setParameterValues(setList,cbsd_list[i])

            #include resposne when sending cbsd to error module
            cbsd_list[i]['response'] = response[resposneMessageType][i]

            addErrorDict(errorCode,errorDict,cbsd_list[i])
            errorList.append(cbsd_list[i]['SN'])
        
        elif typeOfCalling == consts.REG:

            conn = dbConn("ACS_V1_1")
            sqlUpdate = "UPDATE `dp_device_info` SET cbsdID=\""+response['registrationResponse'][i]['cbsdId']+"\",sasStage=\"spectrumInquiry\" WHERE SN=\'"+cbsd_list[i]["SN"]+"\'"
            conn.update(sqlUpdate)

            #nextCalling = conts.SPECTRUM

        elif typeOfCalling == consts.SPECTRUM:

            conn = dbConn("ACS_V1_1")

            #grab all avaialbe channels provided by SAS reply
            channels = response['spectrumInquiryResponse'][0]['availableChannel']
            
            #scans EARFCN list for open channel on SAS
            r = selectFrequency(cbsd_list[i],channels,typeOfCalling)

            #if there is no specturm exit the program(select Frequecny has logged error 400 to FeMS)
            if r == 0:
                return 0

            sqlUpdate = "update `dp_device_info` SET sasStage = 'grant' where cbsdID= \'" + response['spectrumInquiryResponse'][i]['cbsdId'] +"\'"
            conn.update(sqlUpdate)

        elif typeOfCalling == consts.GRANT:            
            conn = dbConn("ACS_V1_1")
            sql_update = "UPDATE `dp_device_info` SET `grantID` = %s , `grantExpireTime` = %s, `operationalState` = \'GRANTED\', `sasStage` = \'heartbeat\' WHERE `cbsdID` = %s"
            conn.update(sql_update,(response['grantResponse'][i]['grantId'],response['grantResponse'][i]['grantExpireTime'],response['grantResponse'][i]['cbsdId']))
            conn.dbClose()


        elif typeOfCalling == consts.HEART or typeOfCalling == consts.SUB_HEART:
           
           heartbeat(cbsd_list[i],response['heartbeatResponse'][i])


        elif typeOfCalling == consts.DEREG:
            pass
            #update sasStage            
            # conn = dbConn("ACS_V1_1")
            # conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.DEREG,cbsd_list[i]['SN']))
            # conn.dbClose()

        elif typeOfCalling == consts.REL:
            pass
            #update sasStage
            # conn = dbConn("ACS_V1_1")
            # conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.REL,cbsd_list[i]['SN']))
            # conn.dbClose()


    if bool(errorDict):
        err.errorModule(errorDict,typeOfCalling)
        cbsd_list[:] = [cbsd for cbsd in cbsd_list if not hasError(cbsd,errorList)]

    if bool(cbsd_list):
        #update sasStage for subheart
        if typeOfCalling == consts.HEART:
            conn = dbConn(consts.DB)
            for cbsd in cbsd_list:
                conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.SUB_HEART,cbsd['SN']))
            conn.dbClose()


        nextCalling = getNextCalling(typeOfCalling)
        #should rather make cbsd a class
        #update cbsd list properties
        
        if (nextCalling != False):
            conn = dbConn("ACS_V1_1")
            updated_cbsd_list = conn.select("SELECT * FROM dp_device_info WHERE sasStage = %s",nextCalling)
            conn.dbClose()
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

    if method == consts.SUB_HEART:
        method = consts.HEART

    try:
        return requests.post(app.config['SAS']+method, 
        cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
        verify=('googleCerts/ca.cert'),
        json=request)
        # timeout=5

        # cert=('certs/client.cert','certs/client.key'),
        # verify=('certs/ca.cert'),
        # json=request,
        # timeout=5)
        
    except Exception as e:
        print(f"your connection has failed: {e}")
        return False

def getOpState(cbsd):

    if expired(cbsd['transmitExpireTime'] ):
        opState = 'GRANTED'
        conn = dbConn("ACS_V1_1")
        conn.update("UPDATE dp_device_info SET operationalState = 'GRANTED' WHERE SN = %s",cbsd['SN'])
        conn.dbClose()
        #turn RF Off
        # cbsdAction(cbsd['SN'],"RF_OFF",str(datetime.now()))
        if cbsd['AdminState'] != 0:
            setList  = [consts.ADMIN_POWER_OFF]
            #power off ASAP
            setParameterValues(setList,cbsd)
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

def MHZtoEARFCN(MHz):
    
    #take low freq in MHz and 10(to get the middle freq)
    # MHz = int(cbsd['lowFrequency']) + 10
    #then convert to EARFCN
    EARFCN = math.ceil(((MHz - 3550)/0.1) + 55240)

    return EARFCN

def EARFCNtoMHZ(earfcn):
    # Function to convert frequency from EARFCN  to MHz 3660 - 3700
    # hz add 6 zeros

    logging.info("////////////////////////////////EARFCN CONVERTION\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'")
    print("EARFCN: " + str(earfcn))
    if int(earfcn) > 56739 or int(earfcn) < 55240:
        logging.info("SPECTRUM IS OUTSIDE OF BOUNDS")
        F = 0
    elif earfcn == 55240:
        F = 3560
    elif earfcn == 56739:
        F = 3690
    else:
        F = math.ceil(3550 + (0.1 * (int(earfcn) - 55240)))

    #return middle frequency
    return F

def updateMaxEirp(cbsd):
    conn = dbConn(consts.DB)
    conn.update("UPDATE dp_device_info SET maxEIRP = %s WHERE SN = %s",( (cbsd['TxPower'] + cbsd['antennaGain']), str(cbsd['SN'])))
    cbsd['maxEIRP'] = (cbsd['TxPower'] + cbsd['antennaGain'])
    conn.dbClose()

def EirpToTxPower(maxEirp,cbsd):
    return maxEirp - cbsd['antennaGain']

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
    else:
        return False

def setParameterValues(parameterList,cbsd,typeOfCalling = None):
    #setParamterValues will take in a parameterList and a cbsd.
    #setParamterValues will first check if the cell value matches the paramterList value - in which case no change needs to be made.
    #If a chnage needs to be made we will then add the value to setList and passed to spv db table

    #parameterList is a list of properties to be changed on the cell.
    #cbsd is  dict of current values on the cell 

    #list of parameters to set on the cell 
    startTime = datetime.now()
    setList = []
    try:

        #check if CBSD is connected
        # s.connect((cbsd['IPAddress'], 10500))
        print(f"connected to ip: {cbsd['IPAddress']}")

        

        #add perodic inform to 1 second 
        parameterList.append(consts.PERIODIC_ONE)

        #purge last action(s)
        conn = dbConn("ACS_V1_1")
        conn.update('DELETE FROM fems_spv WHERE SN = %s',cbsd['SN'])

        #for each value change in the parameter list
        for i in range(len(parameterList)):

            #admin state if off
            if parameterList[i]['data_path'] == consts.ADMIN_STATE: 
                if parameterList[i]['data_value'] == 'false':
                    logging.info("Turn RF OFF for %s",cbsd['SN'])
                    conn.update("UPDATE dp_device_info SET AdminState = %s WHERE SN = %s",(0,cbsd['SN']))
                    cbsd['AdminState'] = 0
                else:
                    logging.info("Turn on RF for %s",cbsd['SN'])
                    conn.update("UPDATE dp_device_info SET AdminState = %s WHERE SN = %s",(1,cbsd['SN']))
                    cbsd['AdminState'] = 1
                
            
            #change cell power
            if parameterList[i]['data_path'] == consts.TXPOWER_PATH:
                logging.info("adjust to power to %s dBm",parameterList[i]['data_value'])
                conn.update("UPDATE dp_device_info SET maxEIRP = %s WHERE SN = %s",((parameterList[i]['data_value'] + cbsd['antennaGain']), str(cbsd['SN'])))
                cbsd['TxPower'] = parameterList[i]['data_value']

            #change cell frequency
            if parameterList[i]['data_path'] == consts.EARFCN_LIST:
                #if we are updating earfcn list on cell also update on the database
                logging.info("adjust EARFCN list to %s",parameterList[i]['data_value'])
                #convert earfcn to middle frequency to in MHZ
                MHz = EARFCNtoMHZ(parameterList[i]['data_value'])
                #update plus and minus
                conn.update("UPDATE dp_device_info SET lowFrequency = %s, highFrequency = %s WHERE SN = %s",((MHz -10),(MHz + 10),cbsd['SN']))
                #update cbsd 
                cbsd['lowFrequency'] = MHz - 10
                cbsd['highFrequency'] = MHz + 10


            #update parameters to database for update
            conn.update('INSERT INTO fems_spv(`SN`, `spv_index`,`dbpath`, `setValueType`, `setValue`) VALUES(%s,%s,%s,%s,%s)',(cbsd['SN'],i,parameterList[i]['data_path'],parameterList[i]['data_type'],parameterList[i]['data_value']))


        #place action in apt_action_queue
        cbsdAction(cbsd['SN'],'Set Parameter Value',str(datetime.now()))

        #send connection request to cell
        response = requests.get(cbsd['connreqURL'], auth= HTTPDigestAuth(cbsd['connreqUname'],cbsd['connreqPass']))
        
        #wait until parameters are set
        startTime = datetime.now()
        
        #check if conncetion if accepted by the cell
        if response.status_code == 200:

            logging.info(f"startTime: {startTime}")
            settingParameters = True
            while settingParameters:
                # logging.info(f"Setting Parameters for {cbsd['SN']}")
                endTime = datetime.now()
                # logging.info(f"before query: {endTime}")
                database = conn.select("SELECT * FROM apt_action_queue WHERE SN = %s",cbsd['SN'])
                # logging.info(f"after query: {endTime}")
                
                if database == (): 
                    logging.info(f"Paramters set successfully for {cbsd['SN']}")
                    settingParameters = False
                else:
                    time.sleep(1)
                    endTime = datetime.now()
                    logging.info(f"end time in loop: {endTime}")
        else:
            # remove action from action queue
            conn.update("DELETE FROM apt_action_queue WHERE SN = 'DCE994613163'")
            
            # log connection error to FeMS
            err.log_error_to_FeMS_alarm("CRITICAL",cbsd,"Connection Request Failed",typeOfCalling)    
        conn.dbClose()

    
    except Exception as e:
        #if cell is disconnected log the failure
        logging.info(f"Connection to {cbsd['IPAddress']} failed reason: {e}")
        print(f"Connection to {cbsd['IPAddress']} failed reason: {e}")
    # s.close()
    

    endTime = datetime.now()

    totalTime = endTime - startTime

    print(f"total time take to set paramter for {cbsd['IPAddress']}: {totalTime}")



def getParameterValue(data_model_path,cbsd):
    #data_model_path list of data model path values to get from the cell
    
    conn = dbConn(consts.DB)
    #purge last action
    conn.update('DELETE FROM fems_gpv WHERE SN = %s',cbsd['SN'])

    conn.update('INSERT INTO fems_gpv(`SN`,`gpv_index`,`dbpath`,`username`) VALUES(%s,%s,%s,%s)',(cbsd['SN'],1,data_model_path,"femtocell"))

    cbsdAction(cbsd['SN'],'Get Parameter Value',str(datetime.now()))
    # wait until action is completed
    gettingParameters = True
    while gettingParameters:
        logging.info(f"Getting Parameters for {cbsd['SN']}")
        database = conn.select("SELECT * FROM apt_action_queue WHERE SN = %s",cbsd['SN'])
        
        if database == ():
            logging.info(f"Paramters gotten successfully for {cbsd['SN']}")
            gettingParameters = False
        else:
            time.sleep(5)

    getValue = conn.select("SELECT getValue FROM fems_gpv WHERE SN = %s",cbsd['SN'])

    return getValue
    
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

def selectFrequency(cbsd,channels,typeOfCalling = None):
    #cbsd - dict of cbsd values  
    #channels - List of avaiable channels from the SAS
    #pref - The prefered middle frequecy of the CBSD in hz

    #get earfcn list 
    earfcnList = getEarfcnList(cbsd)

    for earfcn in earfcnList:

        pref = EARFCNtoMHZ(earfcn) * consts.Hz
        low = False
        high = False
        setList = []
        
        for channel in channels:
            if channel['channelType'] == 'GAA':
                lowFreq = pref - consts.TEN_MHz
                if (lowFreq) >= channel['frequencyRange']['lowFrequency'] and (lowFreq) <= channel['frequencyRange']['highFrequency']:
                    low = True

                    if 'maxEirp' in channel:
                        lowChannelEirp = channel['maxEirp']
                #refactor to plusbandWidth(cbsd) to get how many MHz to offset middle freq
                highFreq = pref + consts.TEN_MHz
                if (highFreq) >= channel['frequencyRange']['lowFrequency'] and (highFreq) <= channel['frequencyRange']['highFrequency']:
                    high = True

                    if 'maxEirp' in channel:
                        highChannelEirp = channel['maxEirp']
                if low and high:
                    #convert perf back to EARFCN
                    if earfcn != cbsd['EARFCN'] :
                        selected_earfcn = MHZtoEARFCN((pref/consts.Hz))
                        setList.append({'data_path':consts.EARFCN_LIST,'data_type':'string','data_value':selected_earfcn})
                    else:
                        # update frequency on cbsd and database
                        updateFreq(cbsd,earfcn)
                    
                    if 'maxEirp' in channel:
                    #what if one channels eirp is lower than the other?
                        if lowChannelEirp <= highChannelEirp:
                            maxEirp = lowChannelEirp
                        else: 
                            maxEirp = highChannelEirp
                        if maxEirp < cbsd['maxEIRP']:
                            txPower = maxEirp - cbsd['antennaGain']
                            setList.append({'data_path':consts.TXPOWER_PATH,'data_type':'int','data_value':txPower})
                        
                    if bool(setList):
                        setParameterValues(setList,cbsd)

                    #exit for loops
                    return

    #if no spectrum is found for any channels on cbsd
    if not low or not high:
        print("no spectrum")
        logging.info("no spectrum")
        err.log_error_to_FeMS_alarm("CRITICAL",cbsd,400,consts.SPECTRUM)

        #stop trying
        return 0
        # Handle_Request(cbsd,False)

#pass cbsd; Check if TxPower if txpower is already lower than SAS txpower leave alone
def buildParameterList(parameterDict,cbsd):
    #paramterDict is a dict of data_model_path : value
    #returns a list containing all paramters needed to update the cell with new values
    parameterList = []

    for data_path in parameterDict:

        if data_path == consts.TXPOWER_PATH and parameterDict[data_path] < cbsd['TxPower']:
            parameterList.append({'data_path':consts.TXPOWER_PATH,'data_type':'int','data_value':parameterDict[data_path]})

        if data_path == consts.EARFCN_LIST:
            parameterList.append({'data_path':consts.EARFCN_LIST,'data_type':'string','data_value':parameterDict[data_path]})

    return parameterList


def getEarfcnList(cbsd):
    conn = dbConn(consts.DB)
    
    #collect all parameters from subscription table (update to json ajax send or add more value so there is no case of duplicated entires with same SN in apt_subscription table)
    parameters = conn.select("SELECT parameter FROM apt_subscription WHERE SN = %s",cbsd['SN'])
    
    #convert to json
    parameters = json.loads(parameters[0]['parameter'])
    
    #get eutra values(all possible earfcns provided by user in the subscription table)
    eutra = parameters['EUTRACarrierARFCNDL']['value']
    
    if eutra != '':
        #convert to list
        earfcnList = list(eutra.split(","))

        #convert all values to ints
        earfcnList = [int(i) for i in earfcnList]
            
        #get current earfcn in use(currently assigned to the cell from SON) 
        earfcn = conn.select("SELECT EARFCN FROM dp_device_info WHERE SN = %s",cbsd['SN'])
        #add to the front of the list
        if earfcn not in earfcnList:
            earfcnList.insert(0,earfcn[0]['EARFCN'])

        conn.dbClose()

        return earfcnList
    else:
        earfcn = conn.select("SELECT EARFCN FROM dp_device_info WHERE SN = %s",cbsd['SN'])
        return [earfcn[0]['EARFCN']]

#given an earfcn value and a cbsd; The fucntion will update the low and high freq in the dp_device_info database table
def updateFreq(cbsd,earfcn):
    conn = dbConn(consts.DB)
    MHz = EARFCNtoMHZ(earfcn)
    #update plus and minus
    conn.update("UPDATE dp_device_info SET lowFrequency = %s, highFrequency = %s WHERE SN = %s",((MHz -10),(MHz + 10),cbsd['SN']))
    #update cbsd 
    cbsd['lowFrequency'] = MHz - 10
    cbsd['highFrequency'] = MHz + 10

def heartbeat(cbsd,response):

            conn = dbConn("ACS_V1_1")

            #if opState is granted switch to authorized otherwise stay authorized
            update_operational_state = "UPDATE dp_device_info SET operationalState = CASE WHEN operationalState = 'GRANTED' THEN 'AUTHORIZED' ELSE 'AUTHORIZED' END WHERE cbsdID = \'" + response['cbsdId'] + "\'"
            conn.update(update_operational_state)

            if not expired(response['transmitExpireTime']) and cbsd['AdminState'] != 1:
                print("!!!!!!!!!!!!!!!!GRATNED!!!!!!!!!!!!!!!!!!!!!!!!")
                #then turn on cbsd
                pList = [consts.ADMIN_POWER_ON]
                setParameterValues(pList,cbsd)
                #update operationalState
            
            if expired(response['transmitExpireTime']) and cbsd['AdminState'] == 1:
                #if the heartbeat is expired 
                setList  = [consts.ADMIN_POWER_OFF]
                #power off ASAP
                setParameterValues(setList,cbsd)


            #update transmist expire time
            update_transmit_time = "UPDATE dp_device_info SET transmitExpireTime = \'" + response['transmitExpireTime'] + "\' where cbsdID = \'" + response['cbsdId'] + "\'"
            conn.update(update_transmit_time)
            
            #if response has new grantTime update database
            if 'grantExpireTime' in response:
                updateGrantTime(response['grantExpireTime'],cbsd['SN'])

            conn.dbClose()

def dp_deregister():
    #Get cbsd SNs from FeMS    
    # SNlist = request.form['json']

    # #convert to json
    # SN_json_dict = json.loads(SNlist)

    # #select only the values
    # SNlist = list(SN_json_dict.values())
    # print(f"output of SNlist: {SNlist}")
    SNlist = ['DCE994613163','DCE99461317E']

    #collect all values from databse
    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist)))
    cbsd_list = conn.select(sql,SNlist)

    #Relinquish grant if the cbsd is currently granted to transmit
    rel = []
    print(cbsd_list)
    for cbsd in cbsd_list:
        if cbsd['grantID'] != None:
            rel.append(cbsd)

    if bool(rel):
        Handle_Request(rel,consts.REL)
    Handle_Request(cbsd_list,consts.DEREG)
    return "success"