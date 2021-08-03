import flask
from flask_cors import CORS, cross_origin

app = flask.Flask('run', instance_relative_config=True)
# app.config.from_object('/home/gtadmin/dp_git_failed/dp/config.default')
# app.config.from_pyfile('/home/gtadmin/dp_git_failed/dp/config.py')
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'

def runFlaskSever():
   app.run(port = 8089, use_reloader=False, host='0.0.0.0') 