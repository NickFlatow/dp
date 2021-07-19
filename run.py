from numpy.core.fromnumeric import shape
from numpy.core.numeric import _array_equiv_dispatcher
from lib.dbConn import dbConn
from lib.thread import lockedThread
from lib import sasHandler
from config.default import SAS
from lib.log import logger
from test import app, runFlaskSever
from numpy.ctypeslib import ndpointer

import time
import threading 
import lib.consts as consts
import ctypes

#needed here to make routes work
from lib import routes

#init log class
logger = logger()
hbtimer = 0
#create threadLock
threadLock = threading.Lock()

def registration():
    meth = [consts.REG,consts.SPECTRUM,consts.GRANT]
    # reg = lockedThread("regThread")
    while True:
        print("registration")
        conn = dbConn("ACS_V1_1") 
        cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.REG)
        conn.dbClose()
        if cbsd_list !=():
            sasHandler.Handle_Request(cbsd_list, consts.REG)
        time.sleep(30)

def heartbeat():
        # hb = lockedThread("hbThread")
    while True:
        print("heartbeat")
        conn = dbConn("ACS_V1_1")
        cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.SUB_HEART)
        conn.dbClose()
        if cbsd_list !=():
            sasHandler.Handle_Request(cbsd_list,consts.SUB_HEART)
        time.sleep(30)    

def start():
    # conn = dbConn("ACS_V1_1")
    # conn.update("UPDATE dp_device_info SET sasStage = 'registration', grantID = NULL, operationalState = NULL, transmitExpireTime = NULL, grantExpireTime = NULL WHERE maxEIRP = '19'")
    # conn.dbClose()

    # conn = dbConn("ACS_V1_1")
    # conn.update("UPDATE dp_device_info SET sasStage = 'registration', grantID = NULL, operationalState = NULL, transmitExpireTime = NULL, grantExpireTime = NULL WHERE SN = 'DCE994613163'")
    # conn.dbClose()


    authType = getLicenseAuthType()

    if authType == consts.FUNC_MODE_ALL or authType == consts.FUNC_MODE_DOMAIN_PROXY:

        try:
            #if using args a comma for tuple is needed 
            thread = threading.Thread(target=registration, args=())
            thread.name = 'registration-thread'
            thread.start()
        except Exception as e:
            print(f"Registration thread failed: {e}")
        try:
            #if using args a comma for tuple is needed 
            hbthread = threading.Thread(target=heartbeat, args=())
            hbthread.name = 'heartbeat-thread'
            hbthread.start()

        except Exception as e:
            print(f"Heartbeat thread failed reason: {e}")
        runFlaskSever() 
    else:
        print("Non authorized licesen for Domain Proxy")


def err500():
    conn = dbConn(consts.DB)
    cbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = 'DCE994613163'")
    sasHandler.Handle_Response(cbsd,consts.HB500,consts.SUB_HEART)

def specSelect():
    conn = dbConn(consts.DB)
    cbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = 'DCE994613163'")
    sasHandler.Handle_Response(cbsd,consts.FS1,consts.SPECTRUM)


def reprov(SNlist):
    # #Get cbsd SNs from FeMS    
    # SNlist = request.form['json']

    # #convert to json
    # SNlist = json.loads(SNlist)

    #if granted relinquish grant 
    conn = dbConn(consts.DB)
    cbsd = conn.select("SELECT * FROM dp_device_info WHERE SN = %s",SNlist)


    if cbsd[0]['grantID'] != None:
        conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.REL,cbsd[0]['SN']))
        cbsd[0]['sasStage'] = consts.REL
        sasHandler.Handle_Request(cbsd[0],consts.REL)        

    #update cbsd sasStage for registration
    conn.update("UPDATE dp_device_info SET sasStage = %s WHERE SN = %s",(consts.REPROV,cbsd[0]['SN']))
    conn.dbClose()

def getLicenseAuthType():
    license = ctypes.CDLL("/home/gtadmin/license_control/key_decoder_kim/license.so")

    # license.getFuncVals.restype = ndpointer(dtype=ctypes.c_int, shape=(5,))
    # test = license.getFuncVals()
    # print(f"test: {test}")

    authType = license.getFuncValAuth()

    return authType
    # b = license.getRemainingTime()
    # y = id(z)
    # x = ctypes.cast(y,ctypes.POINTER(z)).value
   
    # ctypes.POINTER(ctypes.c_int)
    # print(x)


 

    # # d = ctypes.cast(a,ctypes.POINTER(a))
    # d = ctypes.cast(abc,ctypes.POINTER(ctypes.c_int))
    

    # print(abc)
    # print(f"getRemainingTime {b}")
    # print(d)

    # fun.myFunction.argtypes = [ctypes.c_int]

    # returnVale = fun.myFunction(4)
    # print(returnVale)

    # data = open("/var/local/pub/license_tmp","r")
    # print(data)

# getLicenseAuthType()

start()
# reprov('DCE99461317E')
# specSelect()



