import lib.consts as consts
from datetime import datetime
from lib import sasHandler
from lib.dbConn import dbConn 


def errorModule(errorDict,typeOfCalling):

    for errorCode in errorDict:

        if errorCode == 100: 
            #dereg and stop trying to register
            conn = dbConn("ACS_V1_1") 
            conn.updateSasStage(consts.DEREG,errorDict[errorCode])
            conn.dbClose() 

            #log error to FeMS
            for cbsd in errorDict[errorCode]:
                log_error_to_FeMS_alarm("CRITICAL",cbsd,errorCode,typeOfCalling)

        if errorCode == 101:
            relinquish = []
            #loop for here
            for cbsd in errorDict[errorCode]:
                #IF GRANTS R E L I N Q U I S H ANY GRANTS
                if cbsd['grantID'] != None:
                    relinquish.append(cbsd)
                #LOG ERROR TO FeMS ALARM TABLE
                log_error_to_FeMS_alarm("CRITICAL",cbsd,errorCode,typeOfCalling)

            #reliquish cbsd with grants
            if bool(relinquish):
                sasHandler.Handle_Request(relinquish,consts.REL)
            #deregister all cbsds
            sasHandler.Handle_Request(errorDict[errorCode],consts.DEREG)

        elif errorCode == 103:
            rel = []
            dereg = []
            #loop for here
            for cbsd in errorDict[errorCode]:
            #if the domain proxy still has a grant with SAS relinquish and reapply
                if cbsd['grantID'] != None:
                    rel.append(cbsd)
                else:
                    #during the reg process just place error in FeMS and deregister to stop trying
                    dereg.append(cbsd)
                    
                if bool(rel):
                    #relinquish grant
                    sasHandler.Handle_Request(rel,consts.REL)
                    #reapply
                    sasHandler.Handle_Request(rel,consts.GRANT)
                
                if bool(dereg):
                    sasHandler.Handle_Request(dereg,consts.DEREG)
        

        elif errorCode == 105:
            #deregister 
            sasHandler.Handle_Request(errorDict[errorCode],consts.DEREG)
            #try to reregister
            sasHandler.Handle_Request(errorDict[errorCode],consts.REG)

        elif errorCode == 400:
            pass

        elif errorCode == 401:
            pass

        elif errorCode == 500:
            rel = []

            #check if any cbsds are expired
            for cbsd in errorDict[errorCode]:
                if sasHandler.expired(cbsd['transmitExpireTime']):
                    rel.append(cbsd)
            #if expired relinuqish grant
            if bool(rel):
                sasHandler.Handle_Request(rel,consts.REL)

            #send all to inquire for new specturm
            sasHandler.Handle_Request(errorDict[errorCode],consts.SPECTRUM)

        elif errorCode == 501:
            for cbsd in errorDict[errorCode]:
        
                if sasHandler.expired(cbsd['transmitExpireTime']):
  
                    if cbsd['AdminState'] == 1:
                        sasHandler.setParameterValue(cbsd['SN'],consts.ADMIN_STATE,'boolean','false')
                    
                    #put cbsd in granted state but still heartbeating
                    conn = dbConn("ACS_V1_1")
                    conn.update("UPDATE dp_device_info SET operationalState = 'GRANTED' WHERE SN = %s",cbsd['SN'])
                    conn.dbClose()
                
                log_error_to_FeMS_alarm("CRITICAL",cbsd,errorCode,typeOfCalling)

        elif errorCode == 502:

            #send grant rel requests
            sasHandler.Handle_Request(errorDict[errorCode],consts.REL)
            #send new grant requets
            sasHandler.Handle_Request(errorDict[errorCode],consts.GRANT)

        else: #error code 102, 200, 201
            #Severity is CRITICAL OR WARNING
            for cbsd in errorDict[errorCode]:
                log_error_to_FeMS_alarm("WARNING",cbsd,errorCode,typeOfCalling)

def log_error_to_FeMS_alarm(severity,cbsd_data,errorCode,typeOfCalling):

    # resposneMessageType = str(typeOfCalling +"Response")
    errorCode = "SAS error code: " + str(errorCode)

    #alarmIdentity is SN, response code and the hour it was reported
    alarmIdentifier = cbsd_data['SN'] +"_"+ str(errorCode) +"_"+ str(datetime.now().hour)

    if(hasAlarmIdentifier(alarmIdentifier)):
        conn = dbConn("ACS_V1_1")
        conn.update("UPDATE apt_alarm_latest SET updateTime = %s,EventTime = %s WHERE AlarmIdentifier = %s" ,(str(datetime.now()),str(datetime.now()),alarmIdentifier ))
        conn.dbClose()
    else: 
        conn = dbConn("ACS_V1_1")
        conn.update("INSERT INTO apt_alarm_latest (CellIdentity,NotificationType,PerceivedSeverity,updateTime,EventTime,SpecificProblem,AlarmIdentifier,Status) values(%s,%s,%s,%s,%s,%s,%s,%s)",(cbsd_data['CellIdentity'],"NewAlarm",severity,str(datetime.now()),str(datetime.now()),errorCode,alarmIdentifier,"New"))
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
