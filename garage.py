import tensorflow as tf
import glob
from dl.workspace import Workspace
from dl.mnst_model import mnstModel
import train.ImgData as jb

ws = Workspace('garage')
model = 'mnst'
modelStore = ws.modelStore(model)

def learn():
    imgWidth = 100
    imgHeight = 76
    labelSize = 2

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
    emptyFolder = '/pirepo/train/empty/ResizeW100/'
    notEmptyFolder = '/pirepo/train/not-empty/ResizeW100/'
    trainData = jb.ImgData(emptyFolder, notEmptyFolder)

    emptyFolder = '/pirepo/test/empty/ResizeW100/'
    notEmptyFolder = '/pirepo/test/not-empty/ResizeW100/'
    testData = jb.ImgData(emptyFolder, notEmptyFolder)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(100):
            batch = trainData.nextBatch(10)
            if i % 50 == 0:
                train_accuracy = accuracy.eval(feed_dict={
                    x: batch[0], y_: batch[1], keep_prob: 1.0})
                print('step %d, training accuracy %g' % (i, train_accuracy))
            train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})

        saver.save(sess, modelStore)
        print("model saved in", modelStore)

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
        jpgs = glob.glob(applyStore + '*.jpg')
        print(applyStore)
        for jpg in jpgs:
            imgArray = jb.img2Array(jpg)
            classification = pred.eval(feed_dict={x: [imgArray], keep_prob: 1.0})
            print(jpg, 'is', classification)


if __name__ == "__main__":
    # learn()
    apply()
