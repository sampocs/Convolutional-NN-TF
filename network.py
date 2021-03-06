import tensorflow as tf 

#MNIST data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
sesh = tf.InteractiveSession()

#Config
learning_rate = 0.001
num_steps = 20000

def main ():
	#INPUT/OUTPUT
	x = tf.placeholder(tf.float32, shape=[None, 784])
	x_image = tf.reshape(x, shape=[-1, 28, 28, 1])
	y_ = tf.placeholder(tf.float32, shape=[None, 10])
		#Four dimensions: [batch, height, width, color channel/depth]
		#Batch size is arbitrary since its one image at a time

	#WEIGHTS
	#Layer 1 (Convolution) - Filter is 5x5, 1 color channel, and 32 of these to map to 32 features
	W_conv1 = weight_variable([5, 5, 1, 32])
	b_conv1 = bias_variable([32])
	#Layer 2 (Convolution) - Filter is 5x5, 32 features -> 64 features
	W_conv2 = weight_variable([5, 5, 32, 64])
	b_conv2 = bias_variable([64])
	#Layer 3 - Fully Connected - There are 64 features each 7x7 
	W_fc1 = weight_variable([7 * 7 * 64, 1024]) #1024 is aribitary (could be any number 256-1024)
	b_fc1 = weight_variable([1024])
	#Layer 5 (Readout) - 1024 flattened features -> 10 outputs 
	W_fc2 = weight_variable([1024, 10])
	b_fc2 = weight_variable([10])

	#BUILD
	#Layer 1: Convolution -> add bias -> ReLU -> max pooling
	h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
	h_pool1 = max_pool_2x2(h_conv1)
	#Layer 2: Same
	h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
	h_pool2 = max_pool_2x2(h_conv2)
	#Layer 3: Flatten to vector -> fully connected -- dimensions: [batch(arbitrary), actual_dimension]
	h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
	h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
	#Layer 4: Dropout - use placeholder so you can turn on during training and off during testing
	keep_prob = tf.placeholder(tf.float32)
	h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
	#Layer 5: Readout (softmax)
	y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2

	#LOSS
	#softmax -> cross entropy -> average -> ADAM optimizer
	cross_entropy = tf.reduce_mean(
		tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
	train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy)

	#TRAIN
	#Compare maximum indexes -> gives list of booleans
	correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
	#Convert booleans to floats and flatten
	accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
	#Initialize variables
	sesh.run(tf.global_variables_initializer())
	#Training iterations
	for i in range(num_steps):
		batch = mnist.train.next_batch(50)
		#Print every 100 iterations
		if (i % 100 == 0):
			train_accuracy = accuracy.eval(feed_dict={
				x: batch[0], y_: batch[1], keep_prob: 1.0})
			print "step: {}/{}, training accuracy: {}".format(i, num_steps, train_accuracy)

		train_step.run(feed_dict={
				x: batch[0], y_: batch[1], keep_prob: 0.5
			})

	#TEST
	print ("test accuracy: {}".format(accuracy.eval(feed_dict={
			x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0
			})))


def weight_variable (shape):
	initial = tf.truncated_normal(shape, stddev=0.1)
	return tf.Variable(initial)

def bias_variable (shape):
	initial = tf.constant(0.1, shape=shape)
	return tf.Variable(initial)

def conv2d (x, W):
	#Expects 4 dimensional tensor; stride is for each dimmension
	return tf.nn.conv2d(x, W, strides=[1,1,1,1], padding='SAME') 

def max_pool_2x2(x):
	#ksize and stride is 2x2 (height x width) and 1 in other dimensions
	return tf.nn.max_pool(x, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')

if __name__ == "__main__":
	main()
	
