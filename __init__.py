import flask
from flask_cors import CORS, cross_origin

app = flask.Flask('run', instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('config.py')
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'
# print("some change")
# app.run(port = app.config["PORT"])

import routes

def runFlaskSever():
   # app.run(port = app.config["PORT"], use_reloader=False) 
   app.run(port = app.config["PORT"], use_reloader=False, host='0.0.0.0') 