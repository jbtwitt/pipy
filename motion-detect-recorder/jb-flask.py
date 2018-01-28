from flask import Flask
from flask import request, Response
from flask import send_file

import os
import json
from classes.MdrSnapshot import MdrSnapshot

mdrConf = json.load(open('garage-flask.json'))
mdrSnapshot = MdrSnapshot(mdrConf)

app = Flask(__name__)
#@app.after_request
def after_request(response):
	#response.headers.add('Keep-Alive', 'timeout=0, max=1')
	response.headers.add('Connection', 'close')
	#response.headers.add('Access-Control-Allow-Origin', '*')
	#response.headers.add('Access-Control-Allow-Headers', 'Access-Control-Allow-Headers, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers')
	#response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
	return response


@app.route("/")
def hello():
	return "Hello World!"

@app.route("/snapshot")
def snapshot():
	asAttachment = False
	if (request.args.get('download') is not None):
		asAttachment = True
	#jpgFile = '/home/pi/camCache/d20160917_232959/f20160918_061321_472937.jpg'
	jpgFile = mdrSnapshot.cameraSnapshot()
	#snapshotSize = os.stat(jpgFile).st_size
	#print "response len: " + str(os.path.getsize(jpgFile))
	response = Response()
	response.headers.add('Connection', 'close')
	#response.headers.add('Keep-Alive', 'timeout=0, max=1')
	response.headers.add('Content-Lenght', str(os.path.getsize(jpgFile)))
	return send_file(jpgFile, mimetype='image/jpg', cache_timeout=0, as_attachment=asAttachment, add_etags=False)
	#return send_file(jpgFile, mimetype='image/jpg', cache_timeout=0, as_attachment=asAttachment)

if __name__ == "__main__":
	app.run(host='0.0.0.0', threaded=True)

