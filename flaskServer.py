import re
from lib.sasClient import SasClient
from lib.GrantManger import GrantManger
from lib.Registration import Registration
from flask_cors import CORS,cross_origin
from flask import Flask,request
from lib.types import MessageTypes
from sasController.router import Router
from sasController.responseProcessor import ResponseProcessor
from models.session import dbSession
from models.models import CBSD
from lib.json import Json
import threading


app = Flask('run', instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('config.py')
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'


for thread in threading.enumerate(): 
    print(f"Flask Server thread loop -- {thread.name}")

gm = GrantManger()
router = Router()
database_session = dbSession()
json = Json()
responseProcessor = ResponseProcessor()

#route for cbsd registration
@app.route('/dp/v1/register', methods=['POST'])
@cross_origin()
def dp_register():

    cbsdSerialNumbers = []

    for serial_number in request.args:
        cbsdSerialNumbers.append(request.args[serial_number])

    if not cbsdSerialNumbers: return "No cbsds Selected"


    with database_session.session_scope() as session:
        cbsds = session.query(CBSD).filter(CBSD.cbsd_serial_number.in_(cbsdSerialNumbers)).all()
        print(cbsds)
        jsonRegRequest = json.buildJsonRequest(cbsds,MessageTypes.REGISTRATION.value)

        #send request
        regResponse = router.routeToSAS(jsonRegRequest,MessageTypes.REGISTRATION)

        #process curl response
        if regResponse.status_code == 200:
            # process SAS resposne
            responseProcessor.processResponse(regResponse.json(),cbsds,MessageTypes.REGISTRATION,session)
        #if updateNode
            #if there node actions handle here
        session.commit()


        #build cbsd class with db model

        #map to json requst

        #get sas response by passing json requst to router
        # router.Run(cbsdSerialNumbers,MessageTypes.REGISTRATION)
        
        #pass sas response to process response

    # dp_deregister()
    return "success"
   


#route for cbsd deregistration
@app.route('/dp/v1/deregister', methods=['POST'])
@cross_origin()
def dp_deregister(test = None):

    return "success"

@app.route('/dp/v1/relinquish', methods=['POST'])
@cross_origin()
def dp_relinquish():
    printTest()


def testFlow(data):

    if gm.getData1():
       gm.setData2(data)
    else:
        gm.setData1(data)

    
def printTest():
    gm.printTest()


def runFlaskSever(): 
    app.run(port = app.config["PORT"], use_reloader=False, host='0.0.0.0')  















