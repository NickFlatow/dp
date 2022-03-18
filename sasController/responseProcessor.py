from datetime import datetime
from lib.types import MessageTypes,ResponseCodes, cbsdAction
from lib.log import logger
from models.models import CBSD
from models.session import dbSession
from cbsdController import executeActions

class ResponseProcessor():

    def __init__(self):
        self.logger = logger()


    def processResponse(self,response:dict,cbsd:CBSD,typeOfCalling:MessageTypes,session:dbSession):
        
        responseType = typeOfCalling.value + 'Response'
        self.logger.log_json(response,len(response[responseType]))
        
        i:int = 0
        for resp in response[responseType]:
            self.mapResposne(resp['response'],cbsd[i],typeOfCalling)
            i += 1

        executeActions.executeAction(session)

    def mapResposne(self,response:dict,cbsd:CBSD,typeOfCalling:MessageTypes) -> cbsdAction:
        if typeOfCalling == MessageTypes.REGISTRATION and response['responseCode'] == ResponseCodes.SUCCESS:
            cbsd.cbsd_id = response['cbsdId']
            cbsd.time_updated = datetime.now()
            #update reg status
        elif typeOfCalling == MessageTypes.REGISTRATION and response['responseCode'] == ResponseCodes.REG_PENDING.value:
            cbsd.cbsd_action = cbsdAction.DEREGISTER.value
            cbsd.time_updated = datetime.now()
        else:
            self.logger.info(f"registration failed for {cbsd.cbsd_serial_number} with responseCode: {response['responseCode']}")