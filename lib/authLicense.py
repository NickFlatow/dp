from lib.dbConn import dbConn
import math

def getSecureInfo():
    conn = dbConn("epc_database")
    secureInfo =conn.select("SELECT * FROM EPCSecureInfo")

    return secureInfo


def testAuthLicense():
    secure = getSecureInfo()

    remainingTime = secure[0]['remainingTime']
    authType = secure[0]['funcVal0']
    eNBNum = 16 * (secure[0]['funcVal2']**2)


    print(f"remainingTime: {remainingTime}, authType: {authType}, eNBNum: {eNBNum}")