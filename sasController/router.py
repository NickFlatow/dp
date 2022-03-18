import requests
import time
from lib import consts
from lib.log import logger
from lib.json import Json
from lib.GrantManger import GrantManger
from lib.types import cbsdAction,MessageTypes
from models.session import dbSession
from models.models import CBSD
from datetime import datetime
import threading

class Router():
    '''
    routes to sas or cbsd
    '''
    
    def __init__(self):
        self.json = Json()
        self.logger = logger()
        self.session = dbSession()
        self.updateNode = False
        # self.typeOfCalling = typeOfCalling

        # self.requester
        
    def Run(self,cbsdSerialNumbers: list,typeOfCalling:str) -> cbsdAction:

        with self.session.session_scope() as session:
            cbsds = session.query(CBSD).filter(CBSD.cbsd_serial_number.in_(cbsdSerialNumbers)).all()
            print(cbsds)
            jsonRegRequest = self.json.buildJsonRequest(cbsds,MessageTypes.REGISTRATION.value)

            #send request
            regResponse = self.routeToSAS(jsonRegRequest,typeOfCalling)

            #process curl response
            if regResponse.status_code == 200:
                # process SAS resposne
                self.processResponse(regResponse.json(),cbsds,typeOfCalling)

            #if updateNode
                #if there node actions handle here
            session.commit()

        for thread in threading.enumerate(): 
            print(f"Registration thread loop -- {thread.name}")

    #return action
    def processResponse(self,response:dict,cbsds:CBSD,typeOfCalling:MessageTypes) -> cbsdAction:
        
        i:int = 0 
        for resp in response:
            #map response to cbsd
            self.mapResponse(typeOfCalling,resp,cbsds[i])
            i += 1

        #pass to cbsd for netconf operation

        #assigned response code and data(transmit, grantId etc) to specfic node 
        #retry,nextAction
        nextAction:cbsdAction

        responseMessageType = typeOfCalling.value + "Response"   
        
        #log response
        self.logger.log_json(response,len(response[responseMessageType]))
    
        # handle error code
        for i in range(len(response[responseMessageType])):
            if response[responseMessageType][i]['response']['responseCode'] == 0:
                cbsds[i].cbsd_id = response[responseMessageType][i]['cbsdId']
                print(datetime.now())
                cbsds[i].time_updated = datetime.now()
            elif response[responseMessageType][i]['response']['responseCode'] == MessageTypes.DEREGISTRATION.value:
                pass
            elif response[responseMessageType][i]['response']['responseCode'] == 200:
                print("200 error code")
                #if response message and response data log here
                cbsds[i].time_updated = datetime.now()


    def mapResponse(self,typeOfCalling:MessageTypes,response:dict, cbsd:CBSD):
        if typeOfCalling == MessageTypes.REGISTRATION:
            pass
            #add response code
            #add cbsdId
    
    
    def process_registration_response():
        pass        
   
    
    def _processResponse():
        pass
        #route to cbsdController for netconf operation 




    def routeToSAS(self,request:dict,typeOfCalling:MessageTypes,retry=5):
        '''
        request: json request to pass to SAS server
        method:  method to pass json request to: registration,spectrum,grant,heartbeat
        '''
        # retries = 0
        # while retries < retry:
        # return consts.REGPASS
        # while True:
        try:
            # return requests.post(consts.SAS+method, 
            # cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
            # verify=('googleCerts/ca.cert'),
            # json=request)
            return requests.post("https://192.168.4.25:5000/v1.2/"+typeOfCalling.value, 
            cert=('certs/client.cert','certs/client.key'),
            verify=('certs/ca.cert'),
            json=request,
            timeout=5)
        except requests.exceptions.RequestException as e:
            # retries += 1
            self.logger.info({f"there has been some exception: {e}"})
            time.sleep(consts.REQ_TIMEOUT)

    def routeToCbsd(cbsdSerailNumbers:list):
        pass