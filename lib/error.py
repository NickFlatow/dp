import lib.consts as consts
from datetime import datetime
from lib import sasHandler
from lib.dbConn import dbConn


def errorModule(errorDict,typeOfCalling):
    send_to_request_list = []
    reReg = False
    for SN in errorDict:
        #collect all cbsd data from database for each SN
        conn = dbConn("ACS_V1_1")
        cbsd_data = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",SN)
        conn.dbClose() 

        errorCode = errorDict[SN]['response']['responseCode']

        if errorCode == 100:
            #dereg and stop trying to register
            conn = dbConn("ACS_V1_1")
            cbsd_data = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",SN)
            conn.dbClose() 

            #log error to FeMS
            log_error_to_FeMS_alarm("CRITICAL",cbsd_data,errorDict[SN]['response'],typeOfCalling)

        if errorCode == 101:

            #IF GRANTS R E L I N Q U I S H ANY GRANTS
            if cbsd_data[0]['grantID'] != None:
                sasHandler.Handle_Request(cbsd_data,consts.REL)
            #DEREGISTER FROM SAS
            sasHandler.Handle_Request(cbsd_data,consts.DEREG)
            #LOG ERROR TO FeMS ALARM TABLE
            log_error_to_FeMS_alarm("CRITICAL",cbsd_data,errorDict[SN]['response'],typeOfCalling)

        elif errorCode == 103:
            
            #if the domain proxy still has a grant with SAS relinquish and reapply
            if cbsd_data[0]['grantID'] != None:
                #stop transmitting
                sasHandler.setParameterValue(cbsd_data[0]['SN'],consts.ADMIN_STATE,'boolean','false')


                #relinquish grant
                sasHandler.Handle_Request(cbsd_data,consts.REL)
                #reapply
                sasHandler.Handle_Request(cbsd_data,consts.GRANT)

            #during the reg process just place error in FeMS and deregister to stop trying
            else:
                sasHandler.Handle_Request(cbsd_data,consts.DEREG)
    

        elif errorCode == 105:
            sasHandler.Handle_Request(cbsd_data,consts.DEREG)
            send_to_request_list.append(SN) 
            reReg = True
            # sasHandler.Handle_Request(cbsd_data,consts.REG)

        #update SAS stage to register
        elif errorCode == 501:
            if sasHandler.expired(errorDict[SN]['transmitExpireTime']):
                    
                    sasHandler.cbsdAction(SN,"RF_OFF,",str(datetime.now()))

                    #put cbsd in granted state but still heartbeating
                    conn = dbConn("ACS_V1_1")
                    conn.update("UPDATE dp_device_info SET operationalState = 'GRANTED' WHERE SN = %s",SN)
                    conn.dbClose()
            
            log_error_to_FeMS_alarm("CRITICAL",cbsd_data,errorDict[SN]['response'],typeOfCalling)

        else: #error code 102, 200, 201
            #Severity is CRITICAL OR WARNING
            log_error_to_FeMS_alarm("WARNING",cbsd_data,errorDict[SN]['response'],typeOfCalling)

        #cbsd_data = ((CBSDSN, {resposne:{responseCode:200,responseMessage:"this is some thing"}}),(CBSDSN, {resposne .....}))

    if bool(send_to_request_list):
        update_sas_stage(send_to_request_list,consts.REG)



def log_error_to_FeMS_alarm(severity,cbsd_data,response,typeOfCalling):

    # resposneMessageType = str(typeOfCalling +"Response")
    errorCode = "SAS error code: " + str(response['responseCode'])

    #alarmIdentity is SN, response code and the hour it was reported
    alarmIdentifier = cbsd_data[0]['SN'] +"_"+ str(response['responseCode']) +"_"+ str(datetime.now().hour)
    
    # print(f"cbsd data: {cbsd_data} \n\n response data: {response}")

    if(hasAlarmIdentifier(alarmIdentifier)):
        conn = dbConn("ACS_V1_1")
        conn.update("UPDATE apt_alarm_latest SET updateTime = %s,EventTime = %s WHERE AlarmIdentifier = %s" ,(str(datetime.now()),str(datetime.now()),alarmIdentifier ))
        conn.dbClose()
    else: 
        conn = dbConn("ACS_V1_1")
        conn.update("INSERT INTO apt_alarm_latest (CellIdentity,NotificationType,PerceivedSeverity,updateTime,EventTime,SpecificProblem,AlarmIdentifier,Status) values(%s,%s,%s,%s,%s,%s,%s,%s)",(cbsd_data[0]['CellIdentity'],"NewAlarm",severity,str(datetime.now()),str(datetime.now()),errorCode,alarmIdentifier,"New"))
        conn.dbClose()


def hasAlarmIdentifier(ai):
    '''
    checks if alarm already exisits in apt_alarm_latest
    '''

    conn = dbConn("ACS_V1_1")
    alarmIdentifier = conn.select('SELECT alarmIdentifier FROM apt_alarm_latest WHERE alarmIdentifier = %s',ai)
    conn.dbClose()

    if alarmIdentifier == ():
        return False
    else:
        return True

def update_sas_stage(cbsds_SN_list,typeOfCalling):
    conn = dbConn("ACS_V1_1")
    conn.updateSasStage(typeOfCalling,cbsds_SN_list)
    pass


    # reposne 200 example
    # REQUEST TIMESTAMP: 2021-05-06T19:14:50 (UTC: 2021-05-07T00:14:50)
    # SAS URL: https://sas.goog/v1.2/registration
    # SAS METHOD: registration
    # JSON REQUEST: 3 CBSDs
    # {
    #   "registrationRequest": [
    #     {
    #       "userId": "AFE-inc",
    #       "fccId": "PIDAS1030A",
    #       "cbsdSerialNumber": "E8585101AAA4",
    #       "cbsdCategory": "B",
    #       "airInterface": {
    #         "radioTechnology": "E_UTRA"
    #       },
    #       "cbsdFeatureCapabilityList": []
    #     },
    #     {
    #       "userId": "AFE-inc",
    #       "fccId": "PIDAS1030A",
    #       "cbsdSerialNumber": "E8585101A98E",
    #       "cbsdCategory": "B",
    #       "airInterface": {
    #         "radioTechnology": "E_UTRA"
    #       },
    #       "cbsdFeatureCapabilityList": []
    #     },
    #     {
    #       "userId": "AFE-inc",
    #       "fccId": "PIDAS1030A",
    #       "cbsdSerialNumber": "E8585101A6CA",
    #       "cbsdCategory": "B",
    #       "airInterface": {
    #         "radioTechnology": "E_UTRA"
    #       },
    #       "cbsdFeatureCapabilityList": []
    #     }
    #   ]
    # }
    # RESPONSE TIMESTAMP: 2021-05-06T19:14:51 (UTC: 2021-05-07T00:14:51)
    # HTTP STATUS: 200 OK
    # JSON RESPONSE:
    # {
    #   "registrationResponse": [
    #     {
    #       "response": {
    #         "responseCode": 200,
    #         "responseMessage": "A Category B device must be installed by a CPI"
    #       }
    #     },
    #     {
    #       "response": {
    #         "responseCode": 200,
    #         "responseMessage": "A Category B device must be installed by a CPI"
    #       }
    #     },
    #     {
    #       "response": {
    #         "responseCode": 200,
    #         "responseMessage": "A Category B device must be installed by a CPI"
    #       }
    #     }
    #   ]
    # }
