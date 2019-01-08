import keras.backend as K
from keras import(
    optimizers,
)
from keras.callbacks import (
    ModelCheckpoint,
    TerminateOnNaN,
)
from keras.layers import (
    Activation,
    add,
    concatenate,
    Dense,
    dot,
    Dropout,
    Embedding,
    Flatten,
    Input,
)
from keras.models import (
    Model,
)
from keras.regularizers import l1, l2

from training.keras.utils.constants import (
    BATCH_SIZE,
    KERAS_MODELS_FORMATTING,
)


def _create_embedding_bias(num_things, thing_in, name):
    return Flatten()(
        Embedding(num_things, 1, input_length=1, name=name)(thing_in)
    )


def _create_starting_layers(num_things, num_features, thing_name, regularizer):
    in_layer = Input(shape=(1,), dtype='int64', name='{}_in'.format(thing_name))
    factors_layer = Embedding(
        num_things,
        num_features,
        input_length=1,
        embeddings_regularizer=regularizer,
        name='{}_factors'.format(thing_name),
    )(in_layer)
    bias = _create_embedding_bias(num_things, in_layer, '{}_bias'.format(thing_name))
    return in_layer, factors_layer, bias


def acceptable_absolute_deviation(y_true, y_pred, max_dev=0.1):
    return K.mean(K.abs(y_true - y_pred) < max_dev)


class CollaborativeFiltering(Model):
    def __init__(
            self,
            num_items, num_users, num_item_features,
            num_neurons=100, dropout_chance=0.5,
    ):
        user_in, user_preferences, user_bias = _create_starting_layers(
            num_users, num_item_features, 'user', l2(10e-5))
        item_in, item_factors, item_bias = _create_starting_layers(
            num_items, num_item_features, 'item', l2(10e-4))

        simple_dot = dot([user_preferences, item_factors], axes=-1)
        simple_dot = add([simple_dot, user_bias, item_bias])
        simple_dot = Flatten()(simple_dot)

        x = concatenate([
            Flatten()(user_preferences), user_bias,
            Flatten()(item_factors), item_bias,
        ])

        x = Dense(num_neurons, activation='relu', use_bias=True)(x)
        x = Dense(num_neurons, activation='relu', use_bias=True)(x)
        x = Dropout(dropout_chance)(x)
        x = Dense(num_neurons, activation=None, use_bias=True)(x)
        x = add([x, simple_dot])
        x = Dense(1, activation=None, name='output')(x)
        super().__init__([item_in, user_in], [simple_dot, x])

    def compile(
            self,
            optimizer=None,
            loss='mean_squared_error',
            metrics=['mean_absolute_error', acceptable_absolute_deviation],
            **kwds
    ):
        optimizer = optimizer or optimizers.Adam(lr=10e-3)
        return super().compile(optimizer, loss=loss, metrics=metrics, **kwds)

    def fit(
            self,
            x, y,
            batch_size=BATCH_SIZE,
            epochs=10,
            verbose=0,
            callbacks=None,
            validation_split=0.1,
            **kwds
    ):
        if callbacks is None:
            callbacks = []
            callbacks.append(ModelCheckpoint(KERAS_MODELS_FORMATTING))
            callbacks.append(TerminateOnNaN())
        return super().fit(
            x, y,
            batch_size=batch_size,
            epochs=epochs,
            verbose=verbose,
            callbacks=callbacks,
            validation_split=validation_split,
            **kwds
        )

class FindingSimilar(): pass
    # but does assume we know that object x is more similar to y than it is to z
