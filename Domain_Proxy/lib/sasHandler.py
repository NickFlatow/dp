import math
import logging
import requests
import time
import lib.error as e
import lib.consts as consts
from lib.log import dpLogger
from lib.dbConn import dbConn
from datetime import datetime
from test import app
# class sasHandler():
#     def __init__(self,cbsd_list):
#         pass

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
            req[requestMessageType].append(
                    {
                        "cbsdId":cbsd['cbsdID'],
                        "grantId":cbsd['grantID'],
                        "operationState":cbsd['operationalState']
                    }
                )
        elif typeOfCalling == consts.DEREG:

            #send relinquishment
            # grantRelinquishmentRequest(cbsds_SN)

            #how to determine if action was complete
            cbsdAction(cbsd['SN'],"RF_OFF",str(datetime.now()))

            req[requestMessageType].append(
                    {
                        "cbsdId":cbsd['cbsdID'],
                    }
                )

        elif typeOfCalling == consts.REL:
            print("REL")
            req[requestMessageType].append(
                {
                    "cbsdId":cbsd['cbsdID'],
                    "grantId":cbsd['grantID']
                }
            )
            #set grant IDs to NULL
            conn = dbConn("ACS_V1_1")
            update_grantID = "UPDATE dp_device_info SET grantID = NULL WHERE SN = %s "
            conn.update(update_grantID,cbsd['SN'])
            conn.dbClose()


    dpLogger.log_json(req,len(cbsd_list))
    SASresponse = contactSAS(req,typeOfCalling)

    # if SASresponse != False:
    #     Handle_Response(cbsd_list,SASresponse.json(),typeOfCalling)

    if SASresponse != False:
        Handle_Response(cbsd_list,SASresponse,typeOfCalling)


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
    
    dpLogger.log_json(response,(len(response[resposneMessageType])))
    
    for i in range(len(response[resposneMessageType])):

        #check for errors in response
        if response[resposneMessageType][i]['response']['responseCode'] != 0:
            # errorList.append(response[resposneMessageType][i][response])
        #    print(response[resposneMessageType][i]['response'])
            errorDict[cbsd_list[i]['SN']] = response[resposneMessageType][i]['response']

        elif typeOfCalling == consts.REG:

            conn = dbConn("ACS_V1_1")
            sqlUpdate = "UPDATE `dp_device_info` SET cbsdID=\""+response['registrationResponse'][i]['cbsdId']+"\",sasStage=\"spectrumInquiry\" WHERE SN=\'"+cbsd_list[i]["SN"]+"\'"
            conn.update(sqlUpdate)

            #nextCalling = conts.SPECTRUM

        elif typeOfCalling == consts.SPECTRUM:
            conn = dbConn("ACS_V1_1")
            # if high frequcy and low frequcy match value(convert to hz) for cbsdId in database then move to next


            #check maxEirp if higher change

            print(len(response['spectrumInquiryResponse'][i]['availableChannel']))

            for channel in response['spectrumInquiryResponse'][i]['availableChannel']:
                 if channel['channelType'] == 'GAA':
                    if channel['maxEirp'] <= cbsd_list[i]['maxEIRP']:
                        print("over")
                    print(channel['frequencyRange']['lowFrequency'],channel['frequencyRange']['highFrequency'])
                       
               
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
            #update sasStage
            conn = dbConn("ACS_V1_1")
            conn.update("UPDATE dp_device_info SET sasStage = %s",consts.DEREG)
            conn.dbClose()


        elif typeOfCalling == consts.REL:
            #update sasStage
            conn = dbConn("ACS_V1_1")
            conn.update("UPDATE dp_device_info SET sasStage = %s",consts.REL)
            conn.dbClose()


    if bool(errorDict):
        e.errorModule(errorDict,typeOfCalling)
        cbsd_list[:] = [cbsd for cbsd in cbsd_list if not hasError(cbsd,errorDict)]

    # if bool(cbsd_list):
    #     nextCalling = getNextCalling(typeOfCalling)
    #     #should rather make cbsd a class
    #     #update cbsd list properties
        
    #     if (nextCalling != False):
    #         conn = dbConn("ACS_V1_1")
    #         updated_cbsd_list = conn.select("SELECT * FROM dp_device_info WHERE sasStage = %s",nextCalling)
    #         Handle_Request(updated_cbsd_list,nextCalling)


def contactSAS(request,method):
    # Function to contact the SAS server
    # request - json array to pass to SAS
    # method - which method SAS you would like to contact registration, spectrum, grant, heartbeat 
    # logger.info(f"{app.config['SAS']}  {method}")


    # try:
    #     return requests.post(app.config['SAS']+method, 
    #     cert=('/home/gtadmin/dp/Domain_Proxy/certs/client.cert','/home/gtadmin/dp/Domain_Proxy/certs/client.key'),
    #     verify=('/home/gtadmin/dp/Domain_Proxy/certs/ca.cert'),
    #     json=request)
    # except Exception as e:
    #     print(f"your connection has failed: {e}")
    #     return False
    return consts.FS1

def cbsdAction(cbsdSN,action,time):
    logging.critical("Triggering CBSD action")
    conn = dbConn("ACS_V1_1")
    sql_action = "INSERT INTO apt_action_queue (SN,Action,ScheduleTime) values(\'"+cbsdSN+"\',\'"+action+"\',\'"+time+"\')"
    logging.critical(cbsdSN + " : SQL cmd " + sql_action)
    conn.update(sql_action)
    conn.dbClose()

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

def hasError(cbsd,errorDict):
    if cbsd['SN'] in errorDict:
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

def setParameterValue(cbsd_SN,data_model_path,setValueType,setValue):
    #purge last action
    conn = dbConn("ACS_V1_1")
    conn.update('DELETE FROM fems_spv WHERE SN = %s',cbsd_SN)

    #insert SN, data_model_path and value into FeMS_spv
    conn.update('INSERT INTO fems_spv(`SN`, `spv_index`,`dbpath`, `setValueType`, `setValue`) VALUES(%s,%s,%s,%s,%s)',(cbsd_SN,1,data_model_path,setValueType,setValue))
    conn.dbClose()
    #call cbsdAction with action as 'Set Parameter Value'
    cbsdAction(cbsd_SN,'Set Parameter Value',str(datetime.now()))
    

def getParameterValue():
    pass
    #check if action is already being executed
    # $sqlQueryStr = "SELECT `Note` FROM `apt_action_queue` WHERE `Action`='".$In_Action."' AND `SN`='".$In_SN."'";
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
