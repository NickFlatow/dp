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

from lib.sasClient import sasClient


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

    try:
        #if using args a comma for tuple is needed 
        thread = threading.Thread(target=test, args=())
        thread.name = 'registration-thread'
        thread.start()
    except Exception as e:
        print(f"Registration thread failed: {e}")
    # try:
    #     #if using args a comma for tuple is needed 
    #     hbthread = threading.Thread(target=heartbeat, args=())
    #     hbthread.name = 'heartbeat-thread'
    #     hbthread.start()

    # except Exception as e:
    #     print(f"Heartbeat thread failed reason: {e}")
        
    runFlaskSever() 



def test():
    # runFlaskSever() 
    s = sasClient()
    #takes cbsd add it to list of cbsds to be registered
    s.create_cbsd('900F0C732A02')
    # s.create_cbsd('DCE99461317E')

    # s.cbsdList[1].sasStage = consts.SPECTRUM


    registration_list = s.filter_sas_stage(consts.REG)
    if registration_list:
        s.makeSASRequest(registration_list,consts.REG)

    
    spectrum_list = s.filter_sas_stage(consts.SPECTRUM)
    if spectrum_list:
        s.makeSASRequest(spectrum_list,consts.SPECTRUM)

        grant_list = s.filter_sas_stage(consts.GRANT)
        s.makeSASRequest(grant_list,consts.GRANT)



        for cbsd in s.cbsdList:
            print(cbsd.sasStage)


        while True:
            heartbeat_list = s.filter_sas_stage(consts.HEART)
            s.makeSASRequest(heartbeat_list,consts.HEART)
            time.sleep(10)


start()
# test()


