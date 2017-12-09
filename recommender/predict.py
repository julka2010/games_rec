import tensorflow as tf

iterations = 200

num_users = 60184
num_items = 45776
num_item_features = 20

correct_rating_diff = 1
reg_param_lambda = 0.1

user_ratings = tf.sparse_placeholder(tf.float32, shape=[None, None])
user_b = tf.placeholder(tf.float32, shape=[])
item_b = tf.placeholder(tf.float32, shape=[num_items, 1])
global_mean = tf.placeholder(tf.float32, shape=[])

features = tf.placeholder(tf.float32, shape=[num_items, num_item_features])
features_biased = tf.concat((features, item_b), 1)

W = tf.Variable(tf.zeros(shape=[num_item_features, 1]), name='user_preferences')
W_with_ones = tf.concat([W, tf.ones([1, 1])], 0)

pred = tf.matmul(features_biased, W_with_ones) + global_mean + user_b
pred_values = tf.gather_nd(pred, user_ratings.indices)
squared_diff = tf.squared_difference(pred_values, user_ratings.values)
squared_error = tf.reduce_sum(squared_diff)

reg_term = reg_param_lambda * tf.matmul(tf.transpose(W), W)
loss = squared_error + reg_term

train_step = tf.train.AdamOptimizer(1e-0).minimize(loss)

correct_pred = tf.less(squared_diff, correct_rating_diff ** 2)
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

H = tf.get_variable('H', shape=[num_items, num_item_features])

saver = tf.train.Saver(var_list={'Items': H})

init = tf.global_variables_initializer()

def main(user, item_bias, mean_rating, user_val=None):
    user_bias = sum(
        [user[1][i] - item_bias[t[0]][0] for i, t in enumerate(user[0])]
        )/len(user[0]) - mean_rating
    training_feed_dict = {
        user_ratings: user,
        user_b: user_bias,
        item_b: item_bias,
        global_mean: mean_rating,
    }
    #For a recommender system predicting scores too high is much worse than
    #predicting scores too low
    #Usually, only top X predictions will be looked at and there the guesses
    #are most surely overoptimistic as any game that got lesser score than the
    #user would give didn't make it to the top suggestions

    with tf.Session() as sess:
        sess.run(init)
        saver.restore(sess, "/home/julka/LP/games_rec/model.ckpt")
        training_feed_dict[features] = H.eval()  #Restored item features
        validation_feed_dict = training_feed_dict.copy()
        validation_feed_dict[user_ratings] = user_val

        for i in range(iterations):
            train_step.run(training_feed_dict)
            if i % 100 == 0:
                print(squared_error.eval(training_feed_dict))
        if user_val is not None:
            return pred.eval(training_feed_dict), squared_error.eval(validation_feed_dict)
        return pred.eval(training_feed_dict),
