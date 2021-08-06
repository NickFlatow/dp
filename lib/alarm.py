from lib.cbsd import CbsdInfo
from lib.dbConn import dbConn
from datetime import datetime


class Alarm:

    def log_error_to_FeMS_alarm(severity: str,cbsd: CbsdInfo,errorCode: int):

        # resposneMessageType = str(typeOfCalling +"Response")
        errorCode = "SAS error code: " + str(errorCode)

        #alarmIdentity is SN, response code and the hour it was reported
        alarmIdentifier = cbsd.SN +"_"+ str(errorCode) +"_"+ str(datetime.now().hour)

        if(hasAlarmIdentifier(alarmIdentifier)):
            conn = dbConn("ACS_V1_1")
            conn.update("UPDATE apt_alarm_latest SET updateTime = %s,EventTime = %s WHERE AlarmIdentifier = %s" ,(str(datetime.now()),str(datetime.now()),alarmIdentifier ))
            conn.dbClose()
        else: 
            conn = dbConn("ACS_V1_1")
            conn.update("INSERT INTO apt_alarm_latest (CellIdentity,NotificationType,PerceivedSeverity,updateTime,EventTime,SpecificProblem,AlarmIdentifier,Status) values(%s,%s,%s,%s,%s,%s,%s,%s)",(cbsd.cellIdenity,"NewAlarm",severity,str(datetime.now()),str(datetime.now()),errorCode,alarmIdentifier,"New"))
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