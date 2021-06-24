import threading
import logging
import time
from lib import sasHandler

threadLock = threading.Lock()

class lockedThread (threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self,cbsds,typeOfCalling):
      logging.info("Starting thread" + self.name)
      # Get lock to synchronize threads
      threadLock.acquire()
      sasHandler.Handle_Request(cbsds,typeOfCalling)
      # Free lock to release next thread
      threadLock.release()
   def hbThread()
