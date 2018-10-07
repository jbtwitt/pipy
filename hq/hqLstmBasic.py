import tensorflow as tf
from tensorflow.contrib import rnn

# from tensorflow.official.mnist import dataset
#import mnist dataset
# from tensorflow.examples.tutorials.mnist import input_data
# mnist=input_data.read_data_sets("/tmp/data/",one_hot=True)

import HqReader
import sys

day='20181003'
ticker='LABU'
hqReader=HqReader.HqReader(ticker, day)

#define constants
#unrolled through 28 time steps
time_steps=10
#hidden LSTM units
num_units=128
#rows of 28 pixels
n_input=6   #VolChg,OP,HP,LP,CP,HL
#learning rate for adam
learning_rate=0.001
#mnist is meant to be classified in 10 classes(0-9).
n_classes=3
#size of batch
batch_size=100

train_x,train_y=hqReader.split_data(train_size=100,time_steps=time_steps,n_classes=n_classes)
print(train_x.shape)
print(train_y.shape)
# sys.exit()

#weights and biases of appropriate shape to accomplish above task
out_weights=tf.Variable(tf.random_normal([num_units,n_classes],dtype=tf.float64))
out_bias=tf.Variable(tf.random_normal([n_classes],dtype=tf.float64))

#defining placeholders
#input image placeholder
x=tf.placeholder("float64",[None,time_steps,n_input])
#input label placeholder
y=tf.placeholder("float64",[None,n_classes])


#processing the input tensor from [batch_size,n_steps,n_input] to "time_steps" number of [batch_size,n_input] tensors
input=tf.unstack(x ,time_steps,1)


#defining the network
lstm_layer=rnn.BasicLSTMCell(num_units,forget_bias=1)
outputs,_=rnn.static_rnn(lstm_layer,input,dtype="float64")


#converting last output of dimension [batch_size,num_units] to [batch_size,n_classes] by out_weight multiplication
prediction=tf.matmul(outputs[-1],out_weights)+out_bias


#loss_function
loss=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction,labels=y))
#optimization
opt=tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss)

#model evaluation
correct_prediction=tf.equal(tf.argmax(prediction,1),tf.argmax(y,1))
accuracy=tf.reduce_mean(tf.cast(correct_prediction,tf.float64))


#initialize variables
init=tf.global_variables_initializer()
with tf.Session() as sess:
    sess.run(init)
    iter=1
    while iter<2:#800:
        # batch_x,batch_y=mnist.train.next_batch(batch_size=batch_size)

        # batch_x=batch_x.reshape((batch_size,time_steps,n_input))

        # sess.run(opt, feed_dict={x: batch_x, y: batch_y})
        sess.run(opt, feed_dict={x: train_x, y: train_y})

        if iter %10==0:
            # acc=sess.run(accuracy,feed_dict={x:batch_x,y:batch_y})
            # los=sess.run(loss,feed_dict={x:batch_x,y:batch_y})
            acc=sess.run(accuracy,feed_dict={x:train_x,y:train_y})
            los=sess.run(loss,feed_dict={x:train_x,y:train_y})
            print("For iter ",iter)
            print("Accuracy ",acc)
            print("Loss ",los)
            print("__________________")

        iter=iter+1


    #calculating test accuracy
    # test_data = mnist.test.images[:128].reshape((-1, time_steps, n_input))
    # test_label = mnist.test.labels[:128]
    # print("Testing Accuracy:", sess.run(accuracy, feed_dict={x: test_data, y: test_label}))
print('done')