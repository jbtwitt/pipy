import tensorflow as tf
import os
import sys
import glob
import json
from dl.workspace import Workspace
from dl.train_store import TrainStore
from dl.mnst_model import mnstModel
# import train.ImgData as jb
import dl.ImgLabelData as jb
from util.JbMail import JbMail

from time import sleep
from urllib.request import urlopen, Request, URLError
import urllib.parse

ws = Workspace('front-door', ['no-visitor', 'visitor'])
model = 'mnst'
modelStore = ws.modelStore(model)

conf = json.load(open(ws.getJson()))
sendmail = conf['sendmail']
myUrl = conf['snapshotUrl']

imgWidth = 100
imgHeight = 76
labelSize = 2

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
        for i in range(100):
            batch = trainData.nextBatch(10, imgWidth)
            if i % 50 == 0:
                train_accuracy = accuracy.eval(feed_dict={
                    x: batch[0], y_: batch[1], keep_prob: 1.0})
                print('step %d, training accuracy %g' % (i, train_accuracy))
            train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})

        saver.save(sess, modelStore)
        print("model saved in", modelStore)

        testBatch = testData.nextBatch(2)
        print('test accuracy %g' % accuracy.eval(feed_dict={
            x: testBatch[0], y_: testBatch[1], keep_prob: 1.0}))


def getSnapshot():
    applyStore = ws.applyStore()
    try:
        # print('getting snapshot download...')
        response = urlopen(myUrl)
        # print(str(response.info()))
        filename = response.getheader('Content-Disposition').split('=')[1]
        data = response.read()
        path = applyStore + filename
        jpgFile = open(path, "wb")
        jpgFile.write(data)
        jpgFile.close()
        response.close()
        return path
    except URLError:
        print ("garage failed at attempt")


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


def prod_apply():
    modelMeta = ws.modelMeta(model)
    print(modelMeta)
    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(modelMeta, clear_devices=True)
        saver.restore(sess, modelStore)
        x = tf.get_collection('x')[0]
        y_conv = tf.get_collection('y_conv')[0]
        keep_prob = tf.get_collection('keep_prob')[0]
        pred = tf.argmax(y_conv, 1)

        while(True):
            jpgFile = getSnapshot()
            if jpgFile is not None:
                imgArray = jb.imgResize2Array(jpgFile, imgWidth)
                print(y_conv.eval(feed_dict={x: [imgArray], keep_prob: 1.0}))
                label, moveTo = classify(pred, x, keep_prob, jpgFile)
                if sendmail:
                    conf['email']['body'] = label
                    jbMail = JbMail(conf)
                    jbMail.attachImages([moveTo])
                    print('sending email ...')
                    # jbMail.send()
                    jbMail.send_ssl()
            sleep(600)
            # break


if __name__ == "__main__":
    cmd = 'apply'
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    if cmd == 'learn':
        learn()
    else:
        prod_apply()
        # getSnapshot()
