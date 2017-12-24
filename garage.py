import tensorflow as tf
import os
import sys
import glob
from dl.workspace import Workspace
from dl.mnst_model import mnstModel
import train.ImgData as jb

from urllib.request import urlopen, Request, URLError
import urllib.parse

ws = Workspace('garage')
model = 'mnst'
modelStore = ws.modelStore(model)

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
    emptyFolder = ws.learnStore('close/')
    notEmptyFolder = ws.learnStore('open/')
    trainData = jb.ImgData(emptyFolder, notEmptyFolder)

    emptyFolder = ws.applyStore('close/')
    notEmptyFolder = ws.applyStore('open/')
    testData = jb.ImgData(emptyFolder, notEmptyFolder)

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

def apply():
    modelMeta = ws.modelMeta(model)
    print(modelMeta)
    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(modelMeta, clear_devices=True)
        saver.restore(sess, modelStore)
        x = tf.get_collection('x')[0]
        y_conv = tf.get_collection('y_conv')[0]
        keep_prob = tf.get_collection('keep_prob')[0]

        pred = tf.argmax(y_conv, 1)
        applyStore = ws.applyStore('')
        predictCloseStore = ws.applyStore('close')
        predictOpenStore = ws.applyStore('open')
        jpgs = glob.glob(applyStore + '*.jpg')
        for jpg in jpgs:
            imgArray = jb.imgResize2Array(jpg, imgWidth)
            classification = pred.eval(feed_dict={x: [imgArray], keep_prob: 1.0})
            if classification[0] == 0:  # close
                mvTo = jpg.replace('/apply\\', '/apply\\close/')
            else:
                mvTo = jpg.replace('/apply\\', '/apply\\open/')
            print(mvTo, classification)
            os.rename(jpg, mvTo)


def prod_apply():
    applyStore = ws.applyStore('')
    try:
        garageUrl = 'http://192.168.2.12:5000/snapshot'
        response = urlopen(garageUrl)
        # print(str(response.info()))
        filename = response.getheader('Content-Disposition').split('=')[1]
        data = response.read()
        jpgFile = open(applyStore + filename, "wb")
        jpgFile.write(data)
        jpgFile.close()
        apply()
    except URLError:
        print ("garage failed at attempt")


if __name__ == "__main__":
    cmd = 'apply'
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    if cmd == 'learn':
        learn()
    else:
        prod_apply()
