from datetime import datetime
from lib.dbConn import dbConn


def errorModule(errorDict,typeOfCalling):
    for SN in errorDict:
        #collect all cbsd data
        conn = dbConn("ACS_V1_1")
        cbsd_data = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",SN)
        conn.dbClose()

        #pass cbsd_data and respose code and message to be logged to FeMS
        log_error_to_FeMS_alarm(cbsd_data,errorDict[SN],typeOfCalling)

    #error_response is a list of key value pairs where the key is the cbsdsn and the value is the numeric response code
    
    #((CBSDSN, {resposne:{responseCode:200,responseMessage:"this is some thing"}}),(CBSDSN, {resposne .....}))

    #determine error number


def log_error_to_FeMS_alarm(cbsd_data,response,typeOfCalling):
    resposneMessageType = str(typeOfCalling +"Response")
    errorCode = "SAS response error code: " + str(response['responseCode'])
    #use cbsd data to populate apt_alarm_latest
    print(f"cbsd data: {cbsd_data} \n\n response data: {response}")
    conn = dbConn("ACS_V1_1")
    conn.update("INSERT INTO apt_alarm_latest (updateTime,EventTime,SpecificProblem,ProbableCause) values(%s,%s,%s,%s)",(str(datetime.now()),str(datetime.now()),errorCode,"Invalid Value"))
    conn.dbClose()

    #include the response code and Message
    pass

def response_200():
    pass
    #200

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
