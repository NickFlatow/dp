from lib.log import dpLogger
import lib.error
from lib.dbConn import dbConn
import lib.consts

def Handle_Response(response,typeOfCalling):
    resposneMessageType = str(typeOfCalling +"Response")
    conn = dbConn("ACS_V1_1")
    sql = 'SELECT * FROM dp_device_info where sasStage = %s' 
    cbsd_list = conn.select(sql,typeOfCalling)
    conn.dbClose()
    errorDict = {}
    
    dpLogger.log_json(response,(len(response[resposneMessageType])))
    
    for i in range(len(response[resposneMessageType])):

        if response[resposneMessageType][i]['response']['responseCode'] != 0: 
            print("error")

        elif typeOfCalling == 'registration':

            conn = dbConn("ACS_V1_1")
            sqlUpdate = "UPDATE `dp_device_info` SET cbsdID=\""+response['registrationResponse'][i]['cbsdId']+"\",sasStage=\"spectrum\" WHERE SN=\'"+cbsd_list[i]["SN"]+"\'"
            conn.update(sqlUpdate)
        
