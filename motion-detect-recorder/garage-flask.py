from flask import Flask
from flask import send_file

import os
import json
from classes.MdrSnapshot import MdrSnapshot
mdrConf = json.load(open('garage-flask.json'))
mdrSnapshot = MdrSnapshot(mdrConf)

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello World!"

@app.route("/snapshot")
def snapshot():
	#jpgFile = '/home/pi/camCache/d20160917_232959/f20160918_061321_472937.jpg'
	jpgFile = mdrSnapshot.cameraSnapshot()
	return send_file(jpgFile, mimetype='image/jpg', as_attachment=True)

if __name__ == "__main__":
	app.run(host='0.0.0.0')

