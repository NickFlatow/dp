import math
import logging
import lib.error as e
import lib.consts as consts
from lib.log import dpLogger
from lib.dbConn import dbConn
from datetime import datetime


def Handle_Response(response,typeOfCalling):
    #HTTP address that is in place e.g.(reg,spectrum,grant heartbeat)
    resposneMessageType = str(typeOfCalling +"Response")
    
    # select all cbsd that are in current step for typeOf Calling
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT * FROM dp_device_info where sasStage = %s' 
    cbsd_list = conn.select(sql,typeOfCalling)
    conn.dbClose()

    #init dict to pass to error module
    errorDict = {}
    
    dpLogger.log_json(response,(len(response[resposneMessageType])))
    
    for i in range(len(response[resposneMessageType])):

        #check for errors in response
        if response[resposneMessageType][i]['response']['responseCode'] != 0:
            # errorList.append(response[resposneMessageType][i][response])
        #    print(response[resposneMessageType][i]['response'])
           errorDict[cbsd_list[i]['SN']] = response[resposneMessageType][i]['response']

        elif typeOfCalling == consts.REG:

            conn = dbConn("ACS_V1_1")
            sqlUpdate = "UPDATE `dp_device_info` SET cbsdID=\""+response['registrationResponse'][i]['cbsdId']+"\",sasStage=\"spectrum\" WHERE SN=\'"+cbsd_list[i]["SN"]+"\'"
            conn.update(sqlUpdate)

        elif typeOfCalling == consts.SPECTRUM:
            conn = dbConn("ACS_V1_1")
            # if high frequcy and low frequcy match value(convert to hz) for cbsdId in database then move to next

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

        elif typeOfCalling == consts.GRANT:
            #TODO Check for measurement Report
            
            conn = dbConn("ACS_V1_1")
            sql_update = "UPDATE `dp_device_info` SET `grantID` = %s , `grantExpireTime` = %s, `operationalState` = \'GRANTED\', `sasStage` = \'heartbeat\' WHERE `cbsdID` = %s"
            conn.update(sql_update,(response['grantResponse'][i]['grantId'],response['grantResponse'][i]['grantExpireTime'],response['grantResponse'][i]['cbsdId']))
            conn.dbClose()

        elif typeOfCalling == consts.HEART: 
                        #TODO what if no reply... lost in the internet
            #TODO check if reply is recieved from all cbsds
            #TODO WHAT IF MEAS REPORT
            #TODO

            conn = dbConn("ACS_V1_1")
            #update operational state to granted/ what if operational state is already authorized
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
                cbsdAction(cbsd_list[i]['SN'],"RF_ON",str(datetime.now()))

        elif typeOfCalling == consts.DEREG:
            pass
            #do nothing for now =

        elif typeOfCalling == consts.REL:
            pass
            #do nothing for now
        
    if bool(errorDict):
        e.errorModule(errorDict,typeOfCalling)

def request(typeOfCalling):
    requestMessageType = str(typeOfCalling +"Request")

    req = {requestMessageType:[]}

    # for i in range(len(response[resposneMessageType])):
    pass
    #build header


def cbsdAction(cbsdSN,action,time):
    logging.critical("Triggering CBSD action")
    conn = dbConn("ACS_V1_1")
    sql_action = "INSERT INTO apt_action_queue (SN,Action,ScheduleTime) values(\'"+cbsdSN+"\',\'"+action+"\',\'"+time+"\')"
    logging.critical(cbsdSN + " : SQL cmd " + sql_action)
    conn.update(sql_action)
    conn.dbClose()
    