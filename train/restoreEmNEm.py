import tensorflow as tf
import ImgData as jb

emptyFolder = '/pirepo/test/empty/ResizeW100/'
notEmptyFolder = '/pirepo/test/not-empty/ResizeW100/'
testData = jb.ImgData(emptyFolder, notEmptyFolder)

modelSavedFolder = "C:\\temp\\saver\\"
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
