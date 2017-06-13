from time import sleep
import datetime
import json

def main(mdrConf):
    from picamera import PiCamera
    res = mdrConf['camera']['resolution']
    camera = PiCamera()
    camera.resolution = (res[0], res[1])
    # camera.framerate = 15
    camera.start_preview()
    sleep(5)
    camera.capture('/home/pi/Desktop/max.jpg')
    camera.stop_preview()

if __name__ == "__main__":
    mdrConf = json.load(open('mdr.json'))
    print datetime.datetime.now()
