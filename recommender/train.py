import tensorflow as tf
from tensorflow.python import debug as tf_debug

num_users = 60184
num_items = 45776
num_item_features = 20
reg_param_lambda = 10

iterations = 1000

#Max difference between predicted rating and true rating
#for prediction to be considered "correct"
correct_rating_diff = 1

#Arbitrary number of users give rating for arbitrary number of items
#Sparse matrix assumed
ratings = tf.sparse_placeholder(tf.float32, shape=[None, None])
global_mean = tf.placeholder(tf.float32, shape=[])

user_b = tf.placeholder(tf.float32, shape=[None, 1])
item_b = tf.placeholder(tf.float32, shape=[None, 1])

#User preferences for features
W = tf.Variable(tf.truncated_normal(
    [num_item_features, num_users], stddev=0.2, mean=0), name='Users')
w_ones = tf.ones((1, num_users))
W_biased = tf.concat([W, tf.transpose(user_b), w_ones], 0)

#Items features
H = tf.Variable(tf.truncated_normal(
    [num_items, num_item_features], stddev=0.2, mean=0), name='Items')
b_ones = tf.ones([num_items, 1])
H_biased = tf.concat([H, item_b, b_ones], 1)

#Our hypothesis
pred = tf.matmul(H_biased, W_biased, name='Hypothesis') + global_mean
pred_values = tf.gather_nd(pred, ratings.indices)

squared_diff = tf.squared_difference(pred_values, ratings.values)
squared_error = tf.reduce_sum(squared_diff)

regularization_term  = reg_param_lambda*(
    tf.reduce_sum(tf.square(W_biased)) + tf.reduce_sum(tf.square(H_biased)))

training_cost = squared_error + regularization_term

correct_pred = tf.less(squared_diff, correct_rating_diff ** 2)
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

train_step = tf.train.AdamOptimizer(1e-1).minimize(training_cost)

saver = tf.train.Saver()

init = tf.global_variables_initializer()

def main(r, user_bias, item_bias, mean_rating=0, save=False):
    training_feed_dict = {
        ratings: r,
        user_b: user_bias,
        item_b: item_bias,
        global_mean: mean_rating
    }
    validation_feed_dict = training_feed_dict.copy()
    with tf.Session() as sess:
        sess.run(init)
        for i in range(iterations):
            train_step.run(training_feed_dict)
            if i % 100 == 0:
                print("Iter %d, training error %g" %
                    (i, training_cost.eval(training_feed_dict)))
            if i % 1000 == 0:
                print("Iter %d, validation accuracy %g" %
                    (i, accuracy.eval(validation_feed_dict)))
        if save:
            saver.save(sess, "/home/julka/LP/games_rec/model.ckpt")
        print("Training accuracy %g" % accuracy.eval(training_feed_dict))
        print("Validation accuracy %g" % accuracy.eval(validation_feed_dict))
