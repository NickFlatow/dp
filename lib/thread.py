import threading
import logging
import time
from lib import consts
from lib import sasHandler
from lib.dbConn import dbConn


threadLock = threading.Lock()

class lockedThread (threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self,cbsds,typeOfCalling):
      logging.info("Starting thread" + self.name)
      # Get lock to synchronize threads
      # threadLock.acquire()
      sasHandler.Handle_Request(cbsds,typeOfCalling)
      # Free lock to release next thread
      # threadLock.release()
   def hbThread(self):
      threadLock.acquire()
      print("heartbeat")
      conn = dbConn("ACS_V1_1")
      cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.HEART)
      conn.dbClose()
      if cbsd_list !=():
            sasHandler.Handle_Request(cbsd_list,consts.HEART)
      threadLock.release()
   def regThread(self):
      print("registration")
      conn = dbConn("ACS_V1_1")
      cbsd_list = conn.select('SELECT * FROM dp_device_info WHERE sasStage = %s',consts.REG)
      conn.dbClose()
      if cbsd_list !=():
         sasHandler.Handle_Request(cbsd_list, consts.REG)
