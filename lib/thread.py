import threading
import time
from lib import sasHandler

threadLock = threading.Lock()

class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self,cbsds,typeOfCalling):
      print("Starting " + self.name)
      # Get lock to synchronize threads
      threadLock.acquire()
      sasHandler.Handle_Request(cbsds,typeOfCalling)
      # Free lock to release next thread
      threadLock.release()
