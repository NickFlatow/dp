from lib.sasClient import SasClient
from lib.GrantManger import GrantManger
from flask_cors import CORS,cross_origin
from flask import Flask,request
import threading

gm = GrantManger()
sasClient = SasClient()


app = Flask('run', instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('config.py')
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'


#route for cbsd registration
@app.route('/dp/v1/register', methods=['POST'])
@cross_origin()
def dp_register():

    cbsdSerialNumbers = []

    for a in request.args:
        cbsdSerialNumbers.append(request.args[a])

    if cbsdSerialNumbers:
        sasClient.sasClientRequestStrategy(cbsdSerialNumbers)

    return "success"


#route for cbsd deregistration
@app.route('/dp/v1/deregister', methods=['POST'])
@cross_origin()
def dp_deregister():


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















