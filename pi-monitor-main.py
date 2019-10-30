import os
from datetime import datetime, timedelta
from time import sleep

REPOS = "/tmp/pi-monitor"
RECYCLE_DAYS = 3
CAMERA_RESOLUTION = [1280, 960]

def createFolder():
    for i in range(RECYCLE_DAYS):
        dir = "%s/%d" % (REPOS, i)
        if not os.path.exists(dir):
            os.makedirs(dir)

def getPath(tm, extName='jpg'):
    return "%s/%d/%s.%s" % (REPOS, (tm.timetuple().tm_yday % RECYCLE_DAYS), tm.strftime("%H%M%S"), extName)

"""
Web Main
"""
def camera_main():
    createFolder()
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

    cameraShot()

"""
Web Main
"""
def web_main():
    from flask import Flask
    from flask import request, Response
    from flask import send_file
    app = Flask(__name__)

    @app.route("/pi-monitor")
    def piMonitor():
        minutesAgo = 0
        if (request.args.get('minutesAgo') is not None):
            minutesAgo = int(request.args.get('minutesAgo'))
        for x in range(5):
            tm = datetime.now() - timedelta(seconds=1)
            if minutesAgo > 0:
                tm = tm - timedelta(minutes=minutesAgo)
            jpgFile = getPath(tm)
            # print(jpgFile)
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
    parser = argparse.ArgumentParser()
    parser.add_argument('mainName', metavar='web_main | camera_main', type=str)
    args = parser.parse_args()
    if args.mainName == 'web_main':
        web_main()
    else:
        camera_main()
