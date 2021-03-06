import os
from datetime import datetime, timedelta
from time import sleep

REPOS = "/tmp/pi-monitor"
RECYCLE_DAYS = 3
CAMERA_RESOLUTION = [800, 608]

def createFolder():
    for i in range(RECYCLE_DAYS):
        dir = "%s/%d" % (REPOS, i)
        if not os.path.exists(dir):
            os.makedirs(dir)

def getPath(tm, extName='jpg'):
    return "%s/%d/%s.%s" % (REPOS, (tm.timetuple().tm_yday % RECYCLE_DAYS), tm.strftime("%H%M%S"), extName)

def cameraShot():
    from picamera import PiCamera
    camera = PiCamera()
    try:
        camera.resolution = CAMERA_RESOLUTION
        # warming
        camera.start_preview()
        jpgName = getPath(datetime.now())
        camera.capture(jpgName)
        camera.stop_preview()

        while True:
            sleep(2)
            jpgName = getPath(datetime.now())
            camera.capture(jpgName)
    finally:
        camera.close()

def camera_main():
    createFolder()
    cameraShot()

"""
Web Main
"""
# from flask import Flask
# from flask import request, Response
# from flask import send_file
# app = Flask(__name__)

# @app.route("/pi-monitor")
# def piMonitor():
# 	for i in range(5):
# 		tm = datetime.now() - timedelta(seconds=i)
# 		jpgFile = getPath(tm)
# 		if os.path.exists(jpgFile) and os.stat(jpgFile).st_size > 1000:
# 			response = Response()
# 			# response.headers.add('Connection', 'close')
# 			response.headers.add('Content-Lenght', str(os.path.getsize(jpgFile)))
# 			return send_file(jpgFile, mimetype='image/jpg', cache_timeout=0, as_attachment=False, add_etags=False)
# 		sleep(0.5)
# 	return ""

def web_main():
    from flask import Flask
    from flask import request, Response
    from flask import send_file
    app = Flask(__name__)

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

    app.run(host='0.0.0.0', threaded=True)

import argparse
if __name__ == "__main__":
    # camera_main()
    # web_main()
    parser = argparse.ArgumentParser()
    parser.add_argument('twoMains', metavar='web_main | camera_main', type=str, nargs='+', help='web_main or camera_main')
    # parser.add_argument('-ticker', help='ticker')
    args = parser.parse_args()
    # print(vars(args)[''])
    print(args.twoMains)
