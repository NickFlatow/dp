# import re
from lib import consts
# from lib.cbsd import CbsdInfo
from lib.log import logger
from models.models import CBSD



class Json():

    def __init__(self):
        self.logger = logger()

    def buildJsonRequest(self,cbsds: list,typeOfCalling: str) -> dict:
        
        requestMessageType = str(typeOfCalling + "Request")
        
        req = {requestMessageType:[]}

        cbsd:CBSD
        for cbsd in cbsds:

            if typeOfCalling == consts.REG:
                req[requestMessageType].append(
                    {
                        "cbsdSerialNumber": cbsd.cbsd_serial_number,
                        "fccId": cbsd.fcc_id,
                        "cbsdCategory": cbsd.cbsd_category,
                        "userId": cbsd.user_id
                    }
                )

            elif typeOfCalling == consts.SPECTRUM:
                req[requestMessageType].append(
                    { 
                        "cbsdId":cbsd.cbsdID,
                        "inquiredSpectrum":[
                            {
                                "highFrequency":consts.HIGH_FREQUENCY,
                                "lowFrequency":consts.LOW_FREQUENCY
                            }
                        ]
                    }
                )

            elif typeOfCalling == consts.GRANT:
                req[requestMessageType].append(
                        { 
                            "cbsdId":cbsd.cbsdID,
                            "operationParam":{
                                "maxEirp":cbsd.maxEirp,
                                "operationFrequencyRange":{
                                    "lowFrequency":cbsd.lowFrequency * 1000000,
                                    "highFrequency":cbsd.highFrequency * 1000000
                                }
                            }
                        }
                    )

            elif typeOfCalling == consts.HEART:
                req[requestMessageType].append(
                    {
                        "cbsdId":cbsd.cbsdID,
                        "grantId":cbsd.grantID,
                        "operationState":cbsd.operationalState,
                        "grantRenew":False
                    }
                )
            elif typeOfCalling == consts.DEREG:
                req[requestMessageType].append(
                    {
                        "cbsdId":cbsd.cbsdID,
                    }
                )
            elif typeOfCalling == consts.REL:
                req[requestMessageType].append(
                    {
                        "cbsdId":cbsd.cbsdID,
                        "grantId":cbsd.grantID
                    }
                )

        self.logger.log_json(req,len(cbsds))

        return req


    def parseJsonResponse(self,cbsds:list,response:dict,typeOfCalling:str):
        '''Parse Response from SAS and bind data to cbsds'''
        
        #log response
        self.logger.log_json(response,len(cbsds))
        
        responseMessageType = typeOfCalling + "Response"
    
        
        i:int = 0

        for cbsd in cbsds:
            if typeOfCalling == consts.REG:
                
                print(response[responseMessageType][i]['response']['responseCode'])
                
                cbsd.reponseObj.responseCode = response[responseMessageType][i]['response']['responseCode']
                
                if 'responseMessage' in response[responseMessageType][i]:
                    cbsd.reponseObj.responseMessage = response[responseMessageType][i]['response']['responseMessage']
                
                if 'responseData' in response[responseMessageType][i]:
                    cbsd.reponseObj.responseData = response[responseMessageType][i]['response']['responseData']
                
                if 'cbsdId' in response[responseMessageType][i]:
                    cbsd.setCbsdID(response[responseMessageType][i]['cbsdId'])
            
            i += 1

