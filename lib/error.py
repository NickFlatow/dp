import time
import math
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
            if bool(relinquish) and typeOfCalling != consts.REL:
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
                    
                if bool(rel) and typeOfCalling != consts.REL:
                    #relinquish grant
                    sasHandler.Handle_Request(rel,consts.REL)
                    #reapply
                    sasHandler.Handle_Request(rel,consts.GRANT)
                
                if bool(dereg) and typeOfCalling != consts.DEREG:
                        sasHandler.Handle_Request(dereg,consts.DEREG)
        

        elif errorCode == 105:
            #deregister 
            sasHandler.Handle_Request(errorDict[errorCode],consts.DEREG)
            #try to reregister
            sasHandler.Handle_Request(errorDict[errorCode],consts.REG)

        elif errorCode == 106:
            retry = []
            for cbsd in errorDict[errorCode]:
                log_error_to_FeMS_alarm("CRITICAL",cbsd,errorCode,typeOfCalling)

            time.sleep(30)

            #were there any state changes to the cbsd while we were sleeping
            for cbsd in errorDict[errorCode]: 
                #update cbsd from sas
                conn = dbConn(consts.DB)
                c = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",cbsd['SN'])
                conn.dbClose()
                if c[0]['sasStage'] != consts.REL and c[0]['sasStage'] != consts.DEREG:
                    retry.append(c[0])

            if bool(retry):
                sasHandler.Handle_Request(retry,typeOfCalling)

        elif errorCode == 400:
            pass

        elif errorCode == 401:
            pass

        elif errorCode == 500:
            rel = []
            grant = []

            conn = dbConn(consts.DB)
            #check if any cbsds are expired
            for cbsd in errorDict[errorCode]:

                if 'operationParam' in cbsd['response']:
                    #dict to store value changes for the cell
                    pDict = {}
                    #add shorthand for json
                    op = cbsd['response']['operationParam']
                    FR = cbsd['response']['operationParam']['operationFrequencyRange']
                    
                    #set new op paramters on the cell
                    #convert Eirp to txpower build cell parameter list
                    pDict[consts.TXPOWER_PATH] = sasHandler.EirpToTxPower(op['maxEirp'],cbsd)
                    #convert to earfcn and build cell paramter list
                    pDict[consts.EARFCN_LIST] = sasHandler.MHZtoEARFCN( (FR['lowFrequency']/1000000) + 10)

                    paramList = sasHandler.buildParameterList(pDict,cbsd)

                    sasHandler.setParameterValues(paramList,cbsd)

                    cbsd['sasStage'] = consts.GRANT
                    conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.GRANT,cbsd['SN']))
                    grant.append(cbsd)
                else:
                    #if no suggested operational paramters from SAS do spectrum inquiry
                    
                    #reliquish existing grant and apply for new specturm
                    rel.append(cbsd)

            conn.dbClose()
            if bool(rel):
                sasHandler.Handle_Request(rel,consts.REL)
                sasHandler.Handle_Request(rel,consts.SPECTRUM) 
            if bool(grant):
                sasHandler.Handle_Request(grant,consts.GRANT)
                

        elif errorCode == 501:
            for cbsd in errorDict[errorCode]:

                #put cbsd in granted state but still heartbeating
                if cbsd['operationalState'] != 'GRANTED':
                    conn = dbConn("ACS_V1_1")
                    conn.update("UPDATE dp_device_info SET operationalState = 'GRANTED' WHERE SN = %s",cbsd['SN'])
                    cbsd['operationalState'] = 'GRANTED'
                    conn.dbClose()
                log_error_to_FeMS_alarm("CRITICAL",cbsd,errorCode,typeOfCalling)
                #update each cbsd sasStage to sub heartbeat
                conn = dbConn(consts.DB)
                conn.update("UPDATE dp_device_info SET sasStage =%s WHERE SN = %s",(consts.SUB_HEART,cbsd['SN']))
                cbsd['sasStage'] = consts.SUB_HEART
                conn.dbClose()

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


def updateCbsdParameters(cbsd):
    
    #init dict
    setDict = {}
    setDict[cbsd['SN']] = []

    #get TxPower to set on cell(what about negative numbers)
    txPower = cbsd['maxEIRP'] - cbsd['antennaGain']

    setDict[cbsd['SN']].append({'data_path':consts.TXPOWER_PATH,'data_type':'int','data_value':txPower})

    #get earfcn to set on cell
    earfcn = sasHandler.MHZtoEARFCN(cbsd['lowFrequency'] + 10)

    setDict[cbsd['SN']].append({'data_path':consts.EARFCN_LIST,'data_type':'string','data_value':earfcn})

    sasHandler.setParameterValues(setDict,cbsd)





