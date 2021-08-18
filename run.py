import time
import threading 
import lib.consts as consts
from lib.dbConn import dbConn
from config.default import SAS
from flaskConfig import app, runFlaskSever
from lib.sasClient import sasClientClass
from lib.authLicense import License
from flask_cors import cross_origin
from flask import request
import json

sasClient = sasClientClass()

#needed here to make routes work
# from lib.routes import *

#route for cbsd registration
@app.route('/dp/v1/register', methods=['POST'])
@cross_origin()
def dp_register():


    #Get cbsd SNs from FeMS    
    SNlist = request.form['json']

    #convert to json
    SNlist = json.loads(SNlist)

    #collect all values from databse
    conn = dbConn("ACS_V1_1")
    sql = "SELECT * FROM dp_device_info WHERE SN IN ({})".format(','.join(['%s'] * len(SNlist['snDict'])))
    cbsds = conn.select(sql,SNlist['snDict'])
    conn.dbClose()

    sasClient.userRegisterCbsds(cbsds)

    return "success"


#route for cbsd deregistration
@app.route('/dp/v1/deregister', methods=['POST'])
@cross_origin()
def dp_deregister():

    #Get cbsd SNs from FeMS    
    SNlist = request.form['json']

    #convert to json
    SNlist = json.loads(SNlist)

    #send to sasClient to be deregistered
    sasClient.userDeregisterCbsd(SNlist)

    return "success"

def start(l: License):

    # if l.authType == consts.FUNC_MODE_ALL or l.authType == consts.FUNC_MODE_DOMAIN_PROXY and l.remainingtime > 0:
    
    #start heartbeat thread
    try:
        #if using args a comma for tuple is needed 
        thread = threading.Thread(target=heartbeat, args=())
        thread.name = 'heartbeat-thread'
        thread.start()
    except Exception as e:
        print(f"Heartbeat thread failed: {e}")
        
    #run flask server
    runFlaskSever() 


def heartbeat():

    while True:

        sasClient.heartbeat()
        time.sleep(30)


start(License())



