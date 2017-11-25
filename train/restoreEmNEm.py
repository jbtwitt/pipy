import tensorflow as tf
import sys
import glob
import ImgData as jb

modelSavedFolder = "C:\\temp\\saver\\"
category = ['empty', 'not-empty']

def test():
    emptyFolder = '/pirepo/test/empty/ResizeW100/'
    notEmptyFolder = '/pirepo/test/not-empty/ResizeW100/'
    testData = jb.ImgData(emptyFolder, notEmptyFolder)

    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(modelSavedFolder + 'emNemModel.meta', clear_devices=True)
        saver.restore(sess, modelSavedFolder + 'emNemModel')
        x = tf.get_collection('x')[0]
        y_conv = tf.get_collection('y_conv')[0]
        keep_prob = tf.get_collection('keep_prob')[0]

        pred = tf.argmax(y_conv, 1)
        for i in range(7):
            predictBatch = testData.nextBatch()
            print(predictBatch[1][0])
            print( y_conv.eval(feed_dict={x: predictBatch[0], keep_prob: 1.0}) )
            classification = pred.eval(feed_dict={x: predictBatch[0], keep_prob: 1.0})
            print(classification)

def main(runFolder):
    jpgs = glob.glob(runFolder + '*.jpg')
    model = modelSavedFolder + 'emNemModel.meta'
    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(modelSavedFolder + 'emNemModel.meta', clear_devices=True)
        saver.restore(sess, modelSavedFolder + 'emNemModel')
        x = tf.get_collection('x')[0]
        y_conv = tf.get_collection('y_conv')[0]
        keep_prob = tf.get_collection('keep_prob')[0]

        pred = tf.argmax(y_conv, 1)
        for jpg in jpgs:
            imgArray = jb.img2Array(jpg)
            classification = pred.eval(feed_dict={x: [imgArray], keep_prob: 1.0})
            print(jpg, 'is', category[classification[0]])

if __name__ == "__main__":
    runFolder = '/pirepo/run/ResizeW100/'
    runFolder = '/pirepo/test/not-empty/ResizeW100/'
    if len(sys.argv) > 1:
        runFolder = sys.argv[1]
    main(runFolder)
