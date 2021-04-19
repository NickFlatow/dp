import flask

app = flask.Flask('run', instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('config.py')
# app.run(port = app.config["PORT"])


def runFlaskSever():
   app.run(port = app.config["PORT"]) 