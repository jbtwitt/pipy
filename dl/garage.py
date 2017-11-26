import tensorflow as tf
from workspace import Workspace
from mnst_model import mnstModel

ws = Workspace('garage')
modelStore = ws.modelStore('mnst')

imgWidth = 100
imgHeight = 76
labelSize = 2

x = tf.placeholder(tf.float32, [None, imgWidth*imgHeight])
y_conv, keep_prob = mnstModel(x, imgWidth, imgHeight, labelSize)

# for save model
saver = tf.train.Saver()
tf.add_to_collection('x', x)
tf.add_to_collection('keep_prob', keep_prob)
tf.add_to_collection('y_conv', y_conv)

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    # for i in range(500):
    #     batch = trainData.nextBatch(10)
    #     if i % 50 == 0:
    #     train_accuracy = accuracy.eval(feed_dict={
    #         x: batch[0], y_: batch[1], keep_prob: 1.0})
    #     print('step %d, training accuracy %g' % (i, train_accuracy))
    #     train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})

    saver.save(sess, modelStore)
    print("model saved in", modelStore)
