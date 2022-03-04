import flaskServer
import threading

#search db for existing nodes in case of reboot pick up node where left off.....


for thread in threading.enumerate(): 
    print(f"Run thread loop -- {thread.name}")


#set flask server get requests from web page
flaskServer.runFlaskSever()

#set netconf server get requests from enodeb

