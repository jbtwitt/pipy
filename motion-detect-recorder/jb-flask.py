from flask import Flask
from flask import request, Response
from flask import send_file

import os
import json
from time import sleep
from datetime import datetime, timedelta
from classes.MdrSnapshot import MdrSnapshot
import glob

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

from pi_monitor_main import getPath
@app.route("/pi-monitor")
def piMonitor():
	for i in range(5):
		tm = datetime.now() - timedelta(seconds=i)
		jpgFile = getPath(tm)
		if os.path.exists(jpgFile) and os.stat(jpgFile).st_size > 1000:
			response = Response()
			# response.headers.add('Connection', 'close')
			response.headers.add('Content-Lenght', str(os.path.getsize(jpgFile)))
			return send_file(jpgFile, mimetype='image/jpg', cache_timeout=0, as_attachment=False, add_etags=False)
		sleep(0.5)
	return ""

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

@app.route("/daily")
def daily():
	dailyConf = json.load(open('/home/pi/jb/json/daily_mdr.json'))
	folder = dailyConf["snapshotRepository"]
	cmd = request.args.get('cmd')
	if cmd == "list":
		# dailyArchives = glob.glob(folder + "/*.tar.gz")
		dailyArchives = os.listdir(folder)
		return json.dumps(dailyArchives)
	elif cmd == "get":
		file = request.args.get('file')
		return send_file(folder + "/" + file, mimetype='application/tar+gzip', cache_timeout=0, as_attachment=True, add_etags=False)
	elif cmd == "del":
		file = request.args.get('file')
		os.remove(folder + "/" + file)
		return "Done"

if __name__ == "__main__":
	app.run(host='0.0.0.0', threaded=True)

