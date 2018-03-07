from keras import(
    optimizers,
    regularizers,
)
from keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau,
    ModelCheckpoint,
)
import keras.backend as K
from keras.layers import (
    Activation,
    add,
    AlphaDropout,
    BatchNormalization,
    concatenate,
    Dense,
    dot,
    Dropout,
    Embedding,
    Flatten,
    Input,
    merge,
    Reshape,
)
from keras.models import (
    load_model,
    Model,
)
import numpy as np
from scipy.spatial import distance

import utils

def optimizer():
    return optimizers.Adam(lr=0.1)
def callbacks():
    return [
        EarlyStopping(monitor='val_loss', patience=100),
        ReduceLROnPlateau(monitor='loss', patience=2, factor=0.9),
        ModelCheckpoint(utils.MODEL_CHECKPOINT_STRING, period=5),
    ]

def _default_dense(num_neurons, x, reg=1e-4, **kwds):
    x = Dense(
        num_neurons,
        use_bias=True,
        kernel_regularizer=regularizers.l2(reg),
        **kwds
    )(x)
    x = BatchNormalization(axis=-1)(x)
    return Activation('relu')(x)


def collaborative_filtering(num_items, num_users, num_item_features=50):
    def create_bias(num_things, thing_in, name):
        return Flatten()(Embedding(num_things, 1, input_length=1, name=name)(thing_in))
    user_in = Input(shape=(1,), dtype='int64', name='user_in')
    users_preferences = Embedding(
        num_users,
        num_item_features,
        input_length=1,
        embeddings_regularizer=regularizers.l2(1e-5),
        name='users_factors',
    )(user_in)
    user_bias = create_bias(num_users, user_in, 'user_bias')
    item_in = Input(shape=(1,), dtype='int64', name='item_in')
    items_factors = Embedding(
        num_items,
        num_item_features,
        input_length=1,
        embeddings_regularizer=regularizers.l2(1e-4),
        name='items_factors',
    )(item_in)
    item_bias = create_bias(num_items, item_in, 'item_bias')

    aux_x = dot([
        users_preferences,
        items_factors
    ], axes=-1)
    aux_x = Flatten()(aux_x)
    aux_x = add([aux_x, user_bias])
    aux_x = add([aux_x, item_bias])

    x = concatenate([users_preferences, items_factors])
    x = Flatten()(x)
    x = Dense(100, activation='relu', use_bias=True)(x)
    x = Dense(100, activation='relu', use_bias=True)(x)
    x = Dropout(0.5)(x)
    x = Dense(100, activation=None, use_bias=True)(x)
    x = add([x, aux_x])
    x = Activation('relu')(x)
    x = Dense(1)(x)

    model = Model([item_in, user_in], [x, aux_x])
    return model

def close_to(
        things,
        factors_layer_name='items_factors',
        model_path=utils.PATH_TO_BEST_COLLABORATIVE_FILTERING_MODEL,
    ):
    collab_model = load_model(model_path)
    factors_layer = collab_model.get_layer(factors_layer_name)
    factors_model = Model(
            inputs=collab_model.input,
            outputs=factors_layer.output
    )
    things_factors = factors_model.predict([things, things])
    num_things = factors_layer.get_config()['input_dim']
    num_factors = factors_layer.get_config()['output_dim']
    all_things_factors = factors_model.predict(
            [np.arange(num_things), np.arange(num_things)]
    )
    closeness = []
    for interesting_thing_factors in things_factors:
        closeness.append([])
        for thing_factors in all_things_factors:
            closeness[-1].append(distance.minkowski(
                interesting_thing_factors,
                thing_factors,
                num_factors
            ))
    return np.array(closeness)
