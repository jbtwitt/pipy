import tensorflow as tf
import os
import sys
import datetime
from time import sleep
import base64
from urllib.request import urlopen, Request, URLError
import json

from dl.workspace import Workspace
from dl.train_store import TrainStore
from dl.mnst_model import mnstModel
import dl.ImgLabelData as jb
from JbMail import JbMail

imgWidth = 88   # 352 / 4
imgHeight = 60  # 240 / 4
labels = ['car-brother', 'car-vivian', 'empty', 'others']
labelSize = len(labels)

ws = Workspace('nono-parking-lot', labels)
model = 'mnst'
modelStore = ws.modelStore(model)
conf = json.load(open(ws.getJson()))
sendmail = conf['sendmail']
# print(conf)
# sys.exit()

def learn():
    x = tf.placeholder(tf.float32, [None, imgWidth*imgHeight])
    # Define loss and optimizer
    y_ = tf.placeholder(tf.float32, [None, labelSize])
    y_conv, keep_prob, train_step, accuracy = mnstModel(x, y_,
                                                    imgWidth, imgHeight, labelSize)
    # for save model
    saver = tf.train.Saver()
    tf.add_to_collection('x', x)
    tf.add_to_collection('keep_prob', keep_prob)
    tf.add_to_collection('y_conv', y_conv)

    # Import data
    learnStore = TrainStore(ws, 'learn')
    trainData = jb.ImgLabelData(learnStore)

    applyStore = TrainStore(ws, 'apply')
    testData = jb.ImgLabelData(applyStore)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(250):
            batch = trainData.nextBatch(12, imgWidth)
            if i % 50 == 0:
                train_accuracy = accuracy.eval(feed_dict={
                    x: batch[0], y_: batch[1], keep_prob: 1.0})
                print('step %d, training accuracy %g' % (i, train_accuracy))
            train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})

        saver.save(sess, modelStore)
        print("model saved in", modelStore)

        testBatch = testData.nextBatch(100, imgWidth)
        print('test accuracy %g' % accuracy.eval(feed_dict={
            x: testBatch[0], y_: testBatch[1], keep_prob: 1.0}))

def classify(pred, x, keep_prob, jpg):
    applyStore = TrainStore(ws, 'apply')
    labels = applyStore.getLabels()
    imgArray = jb.imgResize2Array(jpg, imgWidth)
    classification = pred.eval(feed_dict={x: [imgArray], keep_prob: 1.0})
    label = labels[classification[0]]
    mvTo = jpg.replace('/apply/', '/apply/' + label + '/')
    print(mvTo, label)
    os.rename(jpg, mvTo)
    return label, mvTo

def prod_apply(username, password, channel):
    modelMeta = ws.modelMeta(model)
    print(modelMeta)
    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(modelMeta, clear_devices=True)
        saver.restore(sess, modelStore)
        x = tf.get_collection('x')[0]
        y_conv = tf.get_collection('y_conv')[0]
        keep_prob = tf.get_collection('keep_prob')[0]
        pred = tf.argmax(y_conv, 1)

        applyStore = TrainStore(ws, 'apply').getRootPath()
        urlSnapshot = UrlSnapshot(applyStore, username, password, channel)
        while(True):
            jpgFile = urlSnapshot.pull()
            if jpgFile is not None:
                label, moveTo = classify(pred, x, keep_prob, jpgFile)
                if sendmail:
                    conf['email']['body'] = label
                    jbMail = jbMail(conf)
                    jbMail.attachImages([moveTo])
                    jbMail.send()
            sleep(15)
            break

class UrlSnapshot:
    def __init__(self, store, username, password, channel=2):
        self.store = store
        url = 'http://114.35.223.91/cgi-bin/net_jpeg.cgi?ch=' + str(channel)
        request = Request(url)
        credentials = ('%s:%s' % (username, password))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))
        request.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))
        self.request = request

    def pull(self):
        response = urlopen(self.request)
        data = response.read()
        timestamp = datetime.datetime.now()
        jpgFilename = self.store + '/at_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.jpg'
        jpgFile = open(jpgFilename, "wb")
        jpgFile.write(data)
        jpgFile.close()
        return jpgFilename

def robot(username, password):
    learnStore = TrainStore(ws, 'learn').getRootPath()
    urlSnapshot = UrlSnapshot(learnStore, username, password, channel=2)
    for i in range(360):
        jpgFilename = urlSnapshot.pull()
        print(jpgFilename)
        sleep(10)

def take_snapshot(username, password):
    url = 'http://114.35.223.91/cgi-bin/net_jpeg.cgi?ch=2'  # + ch  # + '&1514199511126'
    request = Request(url)
    credentials = ('%s:%s' % (username, password))
    encoded_credentials = base64.b64encode(credentials.encode('ascii'))
    request.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))

    learnStore = TrainStore(ws, 'learn').getRootPath()
    for i in range(72):
        response = urlopen(request)
        data = response.read()
        timestamp = datetime.datetime.now()
        jpgFilename = learnStore + '/at_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.jpg'
        jpgFile = open(jpgFilename, "wb")
        jpgFile.write(data)
        jpgFile.close()
        print(jpgFilename)
        sleep(3600)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        usr = sys.argv[1]
        if sys.argv[1] == 'learn':
            learn()
    if len(sys.argv) > 2:
        pwd = sys.argv[2]
    if len(sys.argv) == 3:
        robot(usr, pwd)
    if len(sys.argv) > 3:
        prod_apply(usr, pwd, 2)
