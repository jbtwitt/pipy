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
import tarfile
import zipfile

ws = Workspace('front-door', ['no-visitor', 'car', 'visitor'])
model = 'mnst'
modelStore = ws.modelStore(model)

conf = json.load(open(ws.getJson()))
sendmail = conf['sendmail']
myUrl = conf['snapshotUrl']
trainIteration = conf['ai']['trainIteration']
batchSize = conf['ai']['batchSize']

imgWidth = 100
imgHeight = 76
labelSize = 3

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
        for i in range(trainIteration):
            batch = trainData.nextBatch(batchSize, imgWidth)
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
        print ("front door failed at attempt")


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
                if sendmail and label == 'visitor':
                    conf['email']['body'] = label
                    jbMail = JbMail(conf)
                    jbMail.attachImages([moveTo])
                    print('sending email ...')
                    # jbMail.send()
                    jbMail.send_ssl()
            sleep(30)
            # break

dailyUrl = conf['dailyUrl']
def getDailyList():
    try:
        response = urlopen(dailyUrl + "?cmd=list")
        data = response.read()
        response.close
        return json.loads(data)
    except URLError:
        print ("daily list failed at attempt")

def delDailyArchive(archive):
    try:
        params = urllib.parse.urlencode({'cmd': "del", 'file': archive })
        response = urlopen(dailyUrl + '?' + params)
        data = response.read()
        response.close
        return data
    except URLError:
        print ("daily del failed at attempt")

def getDailyArchive(archive):
    applyStore = ws.applyStore()
    try:
        params = urllib.parse.urlencode({'cmd': "get", 'file': archive })
        response = urlopen(dailyUrl + '?' + params)
        # print(str(response.info()))
        filename = response.getheader('Content-Disposition').split('=')[1]
        data = response.read()
        path = applyStore + filename
        file = open(path, "wb")
        file.write(data)
        file.close()
        response.close()
        return path
    except URLError:
        print ("daily archive failed at attempt")

def extractArchive(path):
    cwd = os.getcwd()
    os.chdir(os.path.dirname(path))
    opener, mode = tarfile.open, 'r:gz'
    try:
        targz = opener(path, mode)
        targz.extractall()
        targz.close()
    finally:
        os.chdir(cwd)
    return os.path.dirname(path) + '/' + os.path.basename(path).split('.')[0]

def dailyClassify(pred, x, keep_prob, jpg, applyFolder):
    applyStore = TrainStore(ws, 'apply')
    labels = applyStore.getLabels()
    imgArray = jb.imgResize2Array(jpg, imgWidth)
    classification = pred.eval(feed_dict={x: [imgArray], keep_prob: 1.0})
    label = labels[classification[0]]
    # mvTo = jpg.replace('/apply/', '/apply/' + label + '/')
    mvTo = applyFolder + '/' + label + '/' + os.path.basename(jpg)
    print(mvTo, label)
    os.rename(jpg, mvTo)
    return label, mvTo

def daily_apply():
    modelMeta = ws.modelMeta(model)
    print(modelMeta)
    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(modelMeta, clear_devices=True)
        saver.restore(sess, modelStore)
        x = tf.get_collection('x')[0]
        y_conv = tf.get_collection('y_conv')[0]
        keep_prob = tf.get_collection('keep_prob')[0]
        pred = tf.argmax(y_conv, 1)

        applyStore = TrainStore(ws, 'apply')
        labels = applyStore.getLabels()
        count = {}
        for label in labels:
            count[label] = 0
        archives = getDailyList()
        print(archives)
        for archive in archives:
            if ".tar.gz" not in archive:
                continue
            file = getDailyArchive(archive)
            dailyApplyFolder = extractArchive(file)
            for label in labels:
                wd = dailyApplyFolder + '/' + label
                if not os.path.exists(wd):
                    os.makedirs(wd)
            print(dailyApplyFolder)
            jpgs = glob.glob(dailyApplyFolder + '/*.jpg')
            for jpgFile in jpgs:
                imgArray = jb.imgResize2Array(jpgFile, imgWidth)
                print(y_conv.eval(feed_dict={x: [imgArray], keep_prob: 1.0}))
                label, moveTo = dailyClassify(pred, x, keep_prob, jpgFile, dailyApplyFolder)
                count[label] = count[label] + 1
                # if sendmail and label == 'visitor':
                #     conf['email']['body'] = label
                #     jbMail = JbMail(conf)
                #     jbMail.attachImages([moveTo])
                #     print('sending email ...')
                #     # jbMail.send()
                #     jbMail.send_ssl()
            delDailyArchive(archive)
            print(count)
            break

if __name__ == "__main__":
    cmd = 'apply'
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    if cmd == 'learn':
        learn()
    elif cmd == 'daily':
        daily_apply()
    else:
        prod_apply()
        # getSnapshot()
