import os
from datetime import datetime, timedelta
from time import sleep

REPOS = "/home/pi/camCache"
RECYCLE_DAYS = 3
CAMERA_RESOLUTION = [640, 480]

def createFolder():
    for i in range(RECYCLE_DAYS):
        dir = "%s/%d" % (REPOS, i)
        if not os.path.exists(dir):
            os.makedirs(dir)

def getPath(tm, cleanPrevious=False, extName='jpg'):
    if cleanPrevious == True:
        for x in range(1,4):
            tm2 = tm + timedelta(seconds=x)
            f = "%s/%d/%s.%s" % (REPOS, (tm2.timetuple().tm_yday % RECYCLE_DAYS), tm2.strftime("%H%M%S"), extName)
            if os.path.exists(f):
                os.remove(f)
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
            # camera warming
            camera.start_preview()
            jpgName = getPath(datetime.now())
            camera.capture(jpgName)
            camera.stop_preview()

            while True:
                sleep(2)
                jpgName = getPath(datetime.now(), cleanPrevious=True)
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
            if os.path.exists(jpgFile):
                jpgStat = os.stat(jpgFile)
                # # if jpgStat.st_size > 1000 and (tm - datetime.fromtimestamp(jpgStat.st_ctime)).total_seconds() < 5:
                # if tm.timetuple().tm_yday != datetime.fromtimestamp(jpgStat.st_ctime).timetuple().tm_yday:
                #     os.remove(jpgFile)
                if jpgStat.st_size > 10000:
                    response = Response()
                    response.headers.add('Content-Lenght', str(jpgStat.st_size))
                    return send_file(jpgFile, mimetype='image/jpg', cache_timeout=0, as_attachment=False, add_etags=False)
            sleep(1)
        return ""

    app.run(host='0.0.0.0', threaded=True)

import sys
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'web_main':
        web_main()
    elif len(sys.argv) > 1 and sys.argv[1] == 'camera_main':
        if len(sys.argv) == 4:
            CAMERA_RESOLUTION = [int(sys.argv[2]), int(sys.argv[3])]
        camera_main()
    else:
        print('Usage: python %s web_main|camera_main [width height]' % (sys.argv[0]))