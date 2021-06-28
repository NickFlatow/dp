from lib.thread import lockedThread
from config.default import SAS
from lib.log import logger
from test import app, runFlaskSever
import time
import threading 
import lib.consts as consts

#needed here to make routes work
from lib import routes

#init log class
logger = logger()
hbtimer = 0
#create threadLock
threadLock = threading.Lock()

def registration():
    meth = [consts.REG,consts.SPECTRUM,consts.GRANT]
    reg = lockedThread("regThread")
    while True:
        reg.regThread()
        time.sleep(30)

def heartbeat():
        hb = lockedThread("hbThread")
        while True:
            hb.hbThread()
            time.sleep(30)    

def start():
    # conn = dbConn("ACS_V1_1")
    # conn.update("UPDATE dp_device_info SET sasStage = 'registration', grantID = NULL, operationalState = NULL, transmitExpireTime = NULL, grantExpireTime = NULL WHERE fccID = '2AQ68T99B226'")
    # conn.dbClose()
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


start()

