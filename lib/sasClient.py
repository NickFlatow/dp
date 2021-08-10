# import json
# import consts
# import requests
# from dbConn import dbConn
# from cbsd import CbsdModelExporter
# from datetime import datetime,timedelta


import json
from logging import error
from math import e
import time
import requests
import threading

from requests.exceptions import ConnectTimeout, ReadTimeout, SSLError
from lib import alarm
from lib.alarm import Alarm 
import lib.consts as consts
from lib.dbConn import dbConn
from lib.cbsd import CbsdInfo, CbsdModelExporter, OneCA
from datetime import datetime,timedelta

# event = threading.Event()


class sasClientClass():
    '''
    One stop shop for all your SAS communication needs.\n
    You got cbsds needing specturm?\n
    We got connections :/
    '''
    def __init__(self):
        #list of cbsd objects
        self.cbsdList = []
        #list of cbsd objects currently heartbeating
        self.heartbeatList = []

        self.alarm = Alarm

        self.event = threading.Event()

    def filter_sas_stage(self,sasStage):

        filtered = []

        for cbsd in self.cbsdList:
            if cbsd.sasStage == sasStage:
                filtered.append(cbsd)
        
        return filtered


    def filter_subsequent_heartbeat(self):

        filtered = []

        for cbsd in self.cbsdList:
            if cbsd.sasStage == consts.HEART and cbsd.subHeart == True:
                filtered.append(cbsd)

        return filtered

    def expired(self,SASexpireTime: str, isGrantTime = False) -> bool:
        '''
        Move to SAS client
        expireTime: str representing UTC expire time\n
        Time expired returns true
        else false
        '''
        if SASexpireTime == None:
            return False

        expireTime = datetime.strptime(SASexpireTime,"%Y-%m-%dT%H:%M:%SZ")

        #Renew grant five minues before it expires
        if isGrantTime:
            expireTime = expireTime - timedelta(seconds=300)
    
        if datetime.utcnow() >= expireTime:
            return True
        else: 
            return False


    def get_cbsd_database_row(self,SN: str) -> dict:
        '''Given a cbsd Serial Number the fucntion will return a dict with cbsd attributes'''
        conn = dbConn(consts.DB)
        cbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",SN)
        conn.dbClose()

        return cbsd

    def addOneCA(self, cbsd: OneCA):
        self.cbsdList.append(cbsd)
        
    def addCbsd(self,sqlCbsd: dict) -> None:

        self.cbsdList.append(CbsdModelExporter.getCbsd(sqlCbsd))

    def getCbsds(self,SNs: dict) -> list:

        cbsds = []

        cbsd: CbsdInfo
        for cbsd in self.cbsdList:
            if cbsd.SN in SNs['snDict']:
                cbsds.append(cbsd)

        return cbsds
            
    

        
    def buildJsonRequest(self,cbsds: list,typeOfCalling: str) -> dict:
        '''
        Builds and logs all json requests to SAS
        '''
        
        requestMessageType = str(typeOfCalling + "Request")
        
        req = {requestMessageType:[]}

        cbsd:CbsdInfo
        for cbsd in cbsds:

            if typeOfCalling == consts.REG:
                req[requestMessageType].append(
                    {
                        "cbsdSerialNumber": cbsd.SN,
                        "fccId": cbsd.fccID,
                        "cbsdCategory": cbsd.cbsdCat,
                        "userId": cbsd.userID
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


        print(json.dumps(req, indent=4))
        return req


    # def SAS_request(self,typeOfCalling: str) -> dict:
    #     '''
    #     passses json to SAS with typeOfCalling method 
    #     returns the resposne from SAS
    #     '''
    #     #filter cbsdList where cbsd.sasStage
         
    #     #build json
    #     sasRequest = self.buildJsonRequest(typeOfCalling)
    #     #contactSAS
    #     response = self.contactSAS(sasRequest,typeOfCalling)

    #     if response.status_code == 200:
    #         return 
    #     print(response)
        
    #     # return sasResponse

    def registrationResposne(self,cbsd: CbsdInfo,sasResponse):
        
        cbsd.setCbsdID(sasResponse['cbsdId'])
        cbsd.setSasStage(consts.SPECTRUM)

    def spectrumResposne(self,cbsd: CbsdInfo,channels):

        channelSelected = cbsd.select_frequency(channels)
        # channelSelected = True

        if channelSelected:
            cbsd.setSasStage(consts.GRANT)
        else: 
            self.err = [cbsd]
            # cbsd.setSasStage("error")

    def grantResposne(self,cbsd: CbsdInfo,sasResponse):
        #set grant expire time
        cbsd.setGrantExpireTime(sasResponse['grantExpireTime'])

        cbsd.grantID = sasResponse['grantId']
        #operationalState to granted
        cbsd.operationalState = 'GRANTED'

        #set sasStage to heartbeat
        cbsd.setSasStage(consts.HEART)

    def heartbeatResposne(self, cbsd: CbsdInfo, sasResponse):
        print(f"utcnow: {datetime.utcnow()}")
        cbsd.setTransmitExpireTime(sasResponse['transmitExpireTime'])

        if self.expired(sasResponse['transmitExpireTime']) and cbsd.adminState == 1:
            cbsd.operationalState = 'GRANTED'
            cbsd.powerOff()
        
        elif not self.expired(sasResponse['transmitExpireTime']) and cbsd.adminState == 0:
            cbsd.powerOn()
            cbsd.operationalState = 'AUTHORIZED'
            cbsd.subHeart = True

    def relinquishmentResponse(self, cbsd: CbsdInfo):
        #TODO move everything from self.deregister?

        cbsd.grantID = None

    def deregistrationResposne(self, cbsd: CbsdInfo):

        cbsd.setCbsdID(None)


    def resendRequest(self, err: dict, errorCode: int, typeOfCalling: str,sleepTime) -> None:

        cbsd: CbsdInfo
        for cbsd in err[errorCode]:
            #log error to FeMS alarm for each cbsd
            self.alarm.log_error_to_FeMS_alarm('WARNING',cbsd,errorCode)

            cbsd.setSasStage(typeOfCalling)
        
        #wait and retry again
        time.sleep(sleepTime)
        # self.event.wait(sleepTime)
        self.registrationFlow()


    def processError(self, err: dict) -> None:
        for errorCode in err.keys():

            #100: Unsupported SAS protocol version
            #101: Blacklist CBSD
            #103: Invalid Parameters
            if errorCode == 100 or errorCode == 101 or errorCode == 103:

                #check if deregistertion or relinquishment is needed
                self.deregisterCbsds(err[errorCode])
                
                cbsd: CbsdInfo
                for cbsd in err[errorCode]:
                    #log error to FeMS page for further user debugging
                    self.alarm.log_error_to_FeMS_alarm("CRITICAL",cbsd,errorCode)

            #105: Deregister
            elif errorCode == 105:
                
                #the cbsd is in a badly desychronized state. reliquish any grants and deregister.
                self.deregisterCbsds(err[errorCode])
                
                #Start fresh and reregister with the SAS
                self.autoRegisterCbsds(err[errorCode])

            #106: Resend The SAS was temporarily unable to fulfill the request
            elif errorCode == 106:

                self.resendRequest(err,errorCode,consts.GRANT,30)

            #200: Pending registration
            elif errorCode == 200:

                self.resendRequest(err,errorCode,consts.REG,30)

            #400 incumbent activity has entered the area between spectrum and grant request(retry spectrum request)
            elif errorCode == 400:

                self.resendRequest(err,errorCode,consts.SPECTRUM,30)

            #401 Grant Conflict
            elif errorCode == 401:

                #relinquish grants
                self.relinquishGrant(err[errorCode])
                #apply for new grant
                self.resendRequest(err,errorCode,consts.GRANT,0)

            #500 Terminate Grant
            elif errorCode == 500:
                
                cbsd: CbsdInfo
                for cbsd in err[errorCode]:
                    #update cbsd with new operational parameters from SAS
                    if not cbsd.updateOperationalParams():
                        #if there are no operational parameters provided
                        
                        #reqlinqusih grant
                        self.relinquishGrant(err[errorCode])
                        #get new spectrum
                        self.makeSASRequest(err[errorCode],consts.SPECTRUM)
                        #apply for new grant
                        self.makeSASRequest(err[errorCode],consts.GRANT)

            #501 Suspend Grant
            elif errorCode == 501:
                
                cbsd: CbsdInfo
                #change heartbeat to granted
                for cbsd in err[errorCode]:
                    cbsd.operationalState = 'GRANTED'
                    cbsd.subHeart = True
                    cbsd.setSasStage(consts.HEART)
                    self.alarm.log_error_to_FeMS_alarm('WARNING',cbsd,errorCode)

            elif errorCode == 502:
                
                cbsd: CbsdInfo
                for cbsd in err[errorCode]:
                    self.alarm.log_error_to_FeMS_alarm('WARNING',cbsd,errorCode)

                self.relinquishGrant(err[errorCode])
                self.makeSASRequest(err[errorCode],consts.GRANT)
            

            #102: Missing required parameter
            #104: Certification error  
            #201: Group Error
            else:
                #no action is required from the domain proxy. Log error to FeMS
                for cbsd in err[errorCode]:
                    alarm.Alarm.log_error_to_FeMS_alarm("WARNING",cbsd,errorCode)
        
        
        # self.errorThread.join()
        print("!!!!!!!! Threading !!!!!!!!!!")
        print(threading.enumerate())
        print("!!!!!!!! Threading !!!!!!!!!!")
        # err.clear()

    def createErrorThread(self,fn,arg):
        try:
            #if using args a comma for tuple is needed 
            self.errorThread = threading.Thread(target=fn, args=(arg,))
            self.errorThread.name = 'error-thread'
            self.errorThread.start()
        except Exception as e:
            print(f"error thread failed: {e}")


    def cbsdError(self,cbsd: CbsdInfo, sasResponse: dict,err: dict) -> bool:

        #makes things more a bit more clear
        responseCode = sasResponse['response']['responseCode']
            
        #if there is an error
        if responseCode != 0:

            #if the transmit time has expired be sure to power off the cbsd ASAP
            if 'transmitExpireTime' in sasResponse and cbsd.adminState == 1:
                if self.expired(sasResponse['transmitExpireTime']):
                    cbsd.powerOff()
            
            #if the sas suggestes new operational paramaters 
            if 'operationParam' in sasResponse:
                cbsd.sasOperationalParams = sasResponse['operationParam']

            #change the sas stage to stop unwanted request being sent to the SAS
            cbsd.setSasStage(consts.ERROR)

            #if the response code already exists in dict
            if responseCode in err.keys():
                #append the list
                err[responseCode].append(cbsd)
            else:
                #if the key does not exist in list create the key and create the list
                err[responseCode] = [cbsd]

            #there was an error
            return True
        else:
            #there was no error
            return False

    def processSasResposne(self, sasResponse: dict, cbsds: list, typeOfCalling: str) -> None:
        #create error dictionry
        err = {}

        responseMessageType = typeOfCalling + "Response"

        print(json.dumps(sasResponse,indent=4))

        #match cbsd with response from SAS
        for i in range(len(cbsds)):
            
            #if there is an error
            if self.cbsdError(cbsds[i],sasResponse[responseMessageType][i],err):
                #skip to the next cbsd in the list
                continue
            
            elif typeOfCalling == consts.REG:
                self.registrationResposne(cbsds[i],sasResponse[responseMessageType][i])
            
            elif typeOfCalling == consts.SPECTRUM:
                self.spectrumResposne(cbsds[i],sasResponse[responseMessageType][i]['availableChannel'])

            elif typeOfCalling == consts.GRANT:
                self.grantResposne(cbsds[i],sasResponse[responseMessageType][i])

            elif typeOfCalling == consts.HEART:
                self.heartbeatResposne(cbsds[i],sasResponse[responseMessageType][i])

            elif typeOfCalling == consts.REL:
                self.relinquishmentResponse(cbsds[i])

            elif typeOfCalling == consts.DEREG:
                self.deregistrationResposne(cbsds[i])
      
        if err:
            print("error")
            self.createErrorThread(self.processError,err)

            # self.processError(err)

    def checkCbsdsTransmitExpireTime(self):
        
        cbsd:CbsdInfo
        hblist = self.filter_sas_stage(consts.HEART)
        if hblist:
            for cbsd in hblist:
                cbsd.isTransmitTimeExpired()

    def contactSAS(self,request:dict,method:str,retry=100):
        '''
        request: json request to pass to SAS server
        method:  method to pass json request to: registration,spectrum,grant,heartbeat
        '''
        timeout = 3
        retries = 0
        while retries < retry:
            try:
                return requests.post("https://test.sas.goog/v1.2/"+method, 
                cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
                verify=('googleCerts/ca.cert'),
                json=request)
                # timeout=5
                # cert=('certs/client.cert','certs/client.key'),
                # verify=('certs/ca.cert'),
                # json=request,
                # timeout=5)
            except(ConnectTimeout,ConnectionError,SSLError,ReadTimeout,ConnectionRefusedError):
                retries = retries + 1
                self.checkCbsdsTransmitExpireTime()
                print('connection to SAS failed')
                print(f'Retry SAS in {timeout} seconds')
                time.sleep(timeout)


    def makeSASRequest(self,cbsds:list,typeOfCalling:str):
        
        req = self.buildJsonRequest(cbsds,typeOfCalling)
        
        sasReponse = self.contactSAS(req,typeOfCalling)
        
        if sasReponse.status_code == 200:
            self.processSasResposne(sasReponse.json(),cbsds,typeOfCalling)
        else:
            print(f"connection error {sasReponse.status_code}")
 
    def cbsdInList(self,cbsdSN: str) -> bool:
        '''
        return True if cbsd is already in self.cbsdList
        '''
        cbsd: CbsdInfo
        for cbsd in self.cbsdList:
            if cbsd.SN == cbsdSN:
                return True


    def updateSasStageBySN(self, SN: str,typeOfCalling):
        cbsd:CbsdInfo
        for cbsd in self.cbsdList:
            if cbsd.SN == SN:
                cbsd.setSasStage(typeOfCalling)

    def userRegisterCbsds(self, cbsds: dict) -> None:
        '''
        Method used to handle registration requested by user
        '''
        
        for cbsd in cbsds:
            #if the cbsd has never been registered
            if not self.cbsdInList(cbsd['SN']):
                #create cbsd class
                self.addCbsd(cbsd)
            else:
                #otherwise just update the stage to registration
                self.updateSasStageBySN(cbsd['SN'],consts.REG)

        self.registrationFlow()

    def autoRegisterCbsds(self, cbsds: list) -> None:
        '''
        Method used by domain proxy to handle registering cbsds
        '''
        cbsd: CbsdInfo
        for cbsd in cbsds:
            cbsd.setSasStage(consts.REG)

        self.registrationFlow()
    
    def registrationFlow(self) -> None:
        
        registration_list = self.filter_sas_stage(consts.REG)
        if registration_list:
            self.makeSASRequest(registration_list,consts.REG)

        spectrum_list = self.filter_sas_stage(consts.SPECTRUM)
        if spectrum_list:
            self.makeSASRequest(spectrum_list,consts.SPECTRUM)

        grant_list = self.filter_sas_stage(consts.GRANT)
        if grant_list:
            self.makeSASRequest(grant_list,consts.GRANT)

        heartbeat_list = self.filter_sas_stage(consts.HEART)
        if heartbeat_list:
            self.makeSASRequest(heartbeat_list,consts.HEART)


    def relinquishGrant(self,cbsds: list) -> None:
        '''
        based on if cbsd has grantID
        this method will set the internal settings for cbsd reqlinquish e.g(powerOff, set times to null, set sas stage)  \n
        then send the reqlinquishment request
        '''
        relinquish = [] 

        cbsd: CbsdInfo
        for cbsd in cbsds:
            if cbsd.grantID != None:
                #set internal settings for cbsd reqlinquish e.g(powerOff, set times to null, set sas stage)
                cbsd.relinquish()
                relinquish.append(cbsd)

        if relinquish:
            self.makeSASRequest(relinquish,consts.REL)

    def deregisterCbsds(self,cbsds:list) -> None:
        '''
        if needed sets the internal settings for cbsd reqlinquish e.g(powerOff, set times to null, set sas stage)  \n
        if needed sets interal settings for cbsd deregister e.g(ensure power is off, set sas stage) \n
        sends the appropriate requests to SAS
        '''
    
        relinquish = []
        deregister = []
        
        cbsd: CbsdInfo
        for cbsd in cbsds:
            if cbsd.grantID != None:
                #set internal settings for cbsd reqlinquish e.g(powerOff, set times to null, set sas stage)
                cbsd.relinquish()
                relinquish.append(cbsd)
            if cbsd.cbsdID != None:
                #set interal settings for cbsd deregister e.g(ensure power is off, set sas stage)
                cbsd.deregister()
                deregister.append(cbsd)
                

        #send requests to SAS for cbsd actions
        if relinquish:
            self.makeSASRequest(relinquish,consts.REL)
        if deregister:
            self.makeSASRequest(cbsds,consts.DEREG)


    def userDeregisterCbsd(self,SNs: dict) -> None:

        cbsds = self.getCbsds(SNs)

        cbsd: CbsdInfo

        for cbsd in cbsds:
            cbsd.setSasStage(consts.DEREG)

        self.deregisterCbsds(cbsds)
            
    def heartbeat(self) -> None:
        #filter for authorized heartbeats
        heartbeat_list = self.filter_subsequent_heartbeat()
        if heartbeat_list:
            # self.event.set()
            self.makeSASRequest(heartbeat_list,consts.HEART)

if __name__ == '__main__':

    s = sasClientClass()
    #takes cbsd add it to list of cbsds to be registered

    conn = dbConn(consts.DB)
    cbsd = conn.select("SELECT * FROM dp_device_info WHERE fccID = %s",'2AQ68T99B226')
    conn.dbClose()

    # s.addCbsd(cbsd[0])
    s.registerCbsds(cbsd)
    # s.create_cbsd('DCE99461317E')

    # s.cbsdList[1].sasStage = consts.SPECTRUM


    registration_list = s.filter_sas_stage(consts.REG)
    if registration_list:
        s.makeSASRequest(registration_list,consts.REG)

    spectrum_list = s.filter_sas_stage(consts.SPECTRUM)
    if spectrum_list:
        s.makeSASRequest(spectrum_list,consts.SPECTRUM)

    grant_list = s.filter_sas_stage(consts.GRANT)
    if grant_list:
        s.makeSASRequest(grant_list,consts.GRANT)

    heartbeat_list = s.filter_sas_stage(consts.HEART)
    if heartbeat_list:
        s.makeSASRequest(heartbeat_list,consts.HEART)


    # for f in registration_list:
    #     print(f.SN)

    #while True:
        #keep heartbeating all cbsds in hb stage
    # s.buildJsonRequest(s.cbsdList,consts.REG)




