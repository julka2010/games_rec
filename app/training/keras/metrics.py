import keras.backend as K

def acceptable_absolute_deviation(y_true, y_pred, max_dev=0.1):
    return K.mean(K.abs(y_true - y_pred) < max_dev)
