<<<<<<< HEAD
def errorModule(reponseDict):
    pass
    #error_response is a list of key value pairs where the key is the cbsdsn and the value is the  resposne json
=======
def errorModule(responseDict):
    print(responseDict)
    #error_response is a list of key value pairs where the key is the cbsdsn and the value is the numeric response code
>>>>>>> structure
    
    #((CBSDSN, {resposne:{responseCode:200,responseMessage:"this is some thing"}}),(CBSDSN, {resposne .....}))

    #determine error number




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
