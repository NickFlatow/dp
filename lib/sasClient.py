# import json
# import consts
# import requests
# from dbConn import dbConn
# from cbsd import CbsdModelExporter
# from datetime import datetime,timedelta

from lib.log import logger
import time
import requests
import threading

from flaskConfig import app
from requests.exceptions import ConnectTimeout, ReadTimeout, SSLError
from lib import alarm
from lib.alarm import Alarm 
import lib.consts as consts
from lib.dbConn import dbConn
from lib.cbsd import CbsdInfo, CbsdModelExporter, OneCA
from datetime import datetime,timedelta
from lib.authLicense import License

class sasClientClass():
    
    def __init__(self):
        #list of cbsd objects
        self.cbsdList = []

        self.alarm = Alarm()

        self.license = License()

        self.logger = logger()

    def filter_sas_stage(self,sasStage):
        filtered = []

        cbsd:CbsdInfo
        for cbsd in self.cbsdList:
            if cbsd.sasStage == sasStage:
                filtered.append(cbsd)
        
        return filtered


    def filter_subsequent_heartbeat(self):

        filtered = []

        cbsd:CbsdInfo
        for cbsd in self.cbsdList:
            if cbsd.sasStage == consts.HEART and cbsd.subHeart == True:
                filtered.append(cbsd)

        return filtered

    def expired(self,SASexpireTime: str, isGrantTime = False) -> bool:
        
        '''
        expireTime: str representing UTC expire time\n
        Time expired returns true
        else false
        '''
        if SASexpireTime == None:
            return False

        expireTime = datetime.strptime(SASexpireTime,"%Y-%m-%dT%H:%M:%SZ")

        #Renew grant five minutes before it expires
        if isGrantTime:
            expireTime = expireTime - timedelta(seconds=300)
    
        if datetime.utcnow() >= expireTime:
            return True
        else: 
            return False


    def addOneCA(self, cbsd: OneCA):
        '''
        Method used for testing 
        '''
        self.cbsdList.append(cbsd)

    def populateList(self):
        '''
        Methoded for the case of reboot or domain proxy to pickup small cell where it has left off in process
        '''


        conn = dbConn("ACS_V1_1")
        cbsds = conn.select("SELECT * FROM dp_device_info")
        conn.dbClose()

        for cbsd in cbsds:
            #if the cbsd has never been registered
            if not self.cbsdInList(cbsd['SN']) and cbsd['sasStage'] != consts.DEREG:
                #create cbsd class
                self.addCbsd(cbsd)

        self.checkCbsdsTransmitExpireTime()
        self.registrationFlow()

    def addCbsd(self,sqlCbsd: dict) -> None:

        self.license:License
        if len(self.cbsdList) >= self.license.numEnB:
            #TODO log error to FeMS
            print("Maximum number of ENB exceeded")
        else:
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

        self.logger.log_json(req,len(cbsds))

        return req

    def registrationResposne(self,cbsd: CbsdInfo,sasResponse):
        
        cbsd.setCbsdID(sasResponse['cbsdId'])
        cbsd.setSasStage(consts.SPECTRUM)

    def spectrumResposne(self,cbsd: CbsdInfo,channels):

        channelSelected = cbsd.select_frequency(channels)
        # channelSelected = True

        if channelSelected:
            cbsd.setSasStage(consts.GRANT)
        else: 
            self.alarm.log_error_to_FeMS_alarm('CRITICAL',cbsd,123)

    def grantResposne(self,cbsd: CbsdInfo,sasResponse):
        #set grant expire time
        cbsd.setGrantExpireTime(sasResponse['grantExpireTime'])

        cbsd.setGrantID(sasResponse['grantId'])
        #operationalState to granted
        cbsd.setOperationalState('GRANTED')

        #set sasStage to heartbeat
        cbsd.setSasStage(consts.HEART)

    def heartbeatResposne(self, cbsd: CbsdInfo, sasResponse):
        cbsd.setTransmitExpireTime(sasResponse['transmitExpireTime'])

        if self.expired(sasResponse['transmitExpireTime']) and cbsd.adminState == 1:
            cbsd.setOperationalState('GRANTED')
            cbsd.powerOff()
        
        elif not self.expired(sasResponse['transmitExpireTime']) and cbsd.adminState == 0:
            cbsd.powerOn()
            cbsd.setOperationalState('AUTHORIZED')
            cbsd.setSubHeart(True)

    def relinquishmentResponse(self, cbsd: CbsdInfo):
     
        cbsd.setSubHeart(False)
        cbsd.setGrantID(None)

    def deregistrationResposne(self, cbsd: CbsdInfo):

        cbsd.setCbsdID(None)
        self.cbsdList.remove(cbsd)

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
                
                opParam = []
                noOpParam = []
                cbsd: CbsdInfo
                for cbsd in err[errorCode]:
                    #update cbsd with new operational parameters from SAS
                    if cbsd.updateOperationalParams(): #apply the new op Params
                        
                        #update grant status
                        cbsd.setSasStage(consts.GRANT)

                        opParam.append(cbsd)
                    #if there are no operational parameters provided    
                    else:
                        noOpParam.append(cbsd)

                if opParam:
                    self.makeSASRequest(opParam,consts.GRANT)
                if noOpParam:
                    self.relinquishGrant(noOpParam)
                    #get new spectrum
                    self.makeSASRequest(noOpParam,consts.SPECTRUM)
                    #apply for new grant
                    self.makeSASRequest(noOpParam,consts.GRANT)

            #501 Suspend Grant
            elif errorCode == 501:
                
                cbsd: CbsdInfo
                #change heartbeat to granted
                for cbsd in err[errorCode]:
                    #TODO make into cbsd function
                    cbsd.setOperationalState('GRANTED')
                    cbsd.setSubHeart(True)
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
                    self.alarm.log_error_to_FeMS_alarm("WARNING",cbsd,errorCode)
        

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

        self.logger.log_json(sasResponse,len(cbsds))

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
            print("Enter Error Module")
            self.createErrorThread(self.processError,err)

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
                return requests.post(app.config['SAS']+method, 
                cert=('googleCerts/AFE01.cert','googleCerts/AFE01.key'),
                verify=('googleCerts/ca.cert'),
                json=request)
                # return requests.post("https://192.168.4.222:5001/v1.2/"+method, 
                # cert=('certs/client.cert','certs/client.key'),
                # verify=('certs/ca.cert'),
                # json=request,
                # timeout=5)

            except(ConnectTimeout,ConnectionError,SSLError,ReadTimeout,ConnectionRefusedError):
                retries = retries + 1
                self.checkCbsdsTransmitExpireTime()
                self.logger.info('connection to SAS failed')
                self.logger.info(f'Retry SAS in {timeout} seconds')
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

        #TODO check database for updates
        #TODO make cbsd method to updatea make changes based on database
        #TODO if grant or heartbeat reqliuish and apply for new grant
        
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

    def getUpdateFromDatabase(self):
        #TODO add rabbitMQ work flow instead
        relinquish = []

        conn = dbConn("ACS_V1_1")
        cbsdUpdate = conn.select("SELECT * FROM dp_device_info")
        conn.dbClose()

        i = 0
        cbsd:CbsdInfo
        for cbsd in self.cbsdList:
            if cbsd.updateFromDatabase(cbsdUpdate[i]):
                relinquish.append(cbsd)
            i = i + 1

        if relinquish:
            self.relinquishGrant(relinquish)
            # self.registrationFlow()
            self.makeSASRequest(relinquish,consts.GRANT)
            self.makeSASRequest(relinquish,consts.HEART)
 
    def heartbeat(self) -> None:

        #keep cbsd data consistant with any changes in FeMS
        self.getUpdateFromDatabase()

        #filter for authorized heartbeats
        heartbeat_list = self.filter_subsequent_heartbeat()
        print(len(heartbeat_list))
        if heartbeat_list:
            self.makeSASRequest(heartbeat_list,consts.HEART)






