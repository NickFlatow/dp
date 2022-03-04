from re import A
import time
from threading import Thread
from lib.types import cbsdAction


class GrantManger(Thread):
    def __init__(self):
        # Thread.__init__(self,None,None,"Grant Manager Main Thread")
        self._kill:bool = False
        self._actionQueue:list = []
        self.heartbeating = False
        self.hbthread:Thread
        self.action_methods = {
            cbsdAction.STARTGRANT:self.startSpecturmInquiry,
            # cbsdAction.DEREGISTER:self.deregister,
            # cbsdAction.RELINQUISH:self.reqlinquish
        }
   
    def run(self):
        print("starting SIQ")
        #poll to start grant
        # while (not self._kill):
        #     if self._actionQueue:
        #         self.handleAction(self._actionQueue[0])
        #         self._actionQueue.pop(0)

        #         #def SIQ.ChannelSelection
        #     print("polling thread")
        #     time.sleep(3)
    

    @property
    def kill(self):
        return self._kill

    @kill.setter
    def kill(self, kill:bool):
        self._kill = kill

    @property
    def actionQueue(self):
        return self._actionQueue

    @actionQueue.setter
    def actionQueue(self, action:cbsdAction):
        print("added action")
        self._actionQueue.append(action)

    def handleAction(self,action:cbsdAction):
        print("handleAction")
        method = self.action_methods[action]
        method()

    def startSpecturmInquiry(self):
        #start spectrum thread
        print("spectrum")

    def _heartbeat(self):
        while not self._kill:
            print("heartbeating")
            time.sleep(30)

    def heartbeat(self):
        if not self.heartbeating:
            self.hbthread = Thread(target=self._heartbeat)
            self.hbthread.name = "heartbeat-thread"
            self.hbthread.start()
            self.heartbeating = True

    # def __init__(self):
    #     self.test = "test"
    #     self.data = []

    # def setData1(self,data):
    #     self.data.append(data)

    # def setData2(self,data):
    #     self.data.append(data)

    # def getData1(self):
    #     return not self.data

    # def printTestCall(self):
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    #         executor.submit(self.printTest)



    def StartChannelSelectionProcess():
        pass