import flask

app = flask.Flask('run', instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('config.py')
# print("some change")
# app.run(port = app.config["PORT"])


def runFlaskSever():
   test = "pig"
   app.run(port = app.config["PORT"]) 