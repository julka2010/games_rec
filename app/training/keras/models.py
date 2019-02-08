import os
import tempfile

from django.core.files import File
import keras.backend as K
from keras import(
    optimizers,
)
from keras.callbacks import (
    Callback,
    EarlyStopping,
    ModelCheckpoint,
    TerminateOnNaN,
)
from keras.layers import (
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
    load_model,
    Model,
)
from keras.regularizers import l2

from training.models import KerasSinglePlayerModel
import training.keras.data_preparation as dp
from training.keras.metrics import acceptable_absolute_deviation
from training.keras.utils.constants import (
    BATCH_SIZE,
    KERAS_MODELS_FORMATTING,
    ITEM_REGULARIZATION_CONSTANT,
    USER_REGULARIZATION_CONSTANT,
    PATH_TO_BEST_COLLABORATIVE_FILTERING_MODEL,
)


class SaveBestToDatabase(Callback):
    """Saves model to filesystem and saves info about it in db."""
    def __init__(self, *args, player_id=None, **kwds):
        self.player_id = player_id
        self.best_val_loss = None
        super().__init__(*args, **kwds)

    def on_epoch_end(self, epoch, logs):
        if (
                self.best_val_loss is None or
                self.best_val_loss > logs.get('val_loss')
        ):
            self.best_val_loss = logs.get('val_loss')
            db_model = KerasSinglePlayerModel(
                epoch=int(epoch),
                loss=logs.get('loss'),
                player_id=self.player_id,
                val_loss=int(logs.get('val_loss')),
            )
            filename = str(abs(hash(self.model))) + '.hdf5'
            temp_file_path = os.path.join(tempfile.gettempdir(), filename)
            self.model.save(temp_file_path)
            db_model.keras_model_file.save(
                filename,
                File(open(temp_file_path, 'rb')),
            )
            db_model.save()


def _create_embedding_bias(num_things, thing_in, input_length, name):
    return Flatten()(
        Embedding(num_things, 1, input_length=input_length, name=name)(thing_in)
    )


def _create_starting_layers(
        num_things,
        num_features,
        input_length,
        thing_name,
        regularizer
    ):
    in_layer = Input(
        shape=(input_length,),
        dtype='int64',
        name='{}_in'.format(thing_name)
    )
    factors_layer = Embedding(
        num_things,
        num_features,
        input_length=input_length,
        embeddings_regularizer=regularizer,
        name='{}_factors'.format(thing_name),
    )(in_layer)
    bias = _create_embedding_bias(
        num_things,
        in_layer,
        input_length,
        '{}_bias'.format(thing_name)
    )
    return in_layer, factors_layer, bias


class CollaborativeFilteringModel():
    _default_compile_parameters = {
        'optimizer': optimizers.Adam(),
        'loss': {
            'highest': 'categorical_crossentropy',
            'values': 'mean_squared_error',
        },
        'loss_weights': {'highest': 1, 'values': 0.001},
        'metrics': {
            'highest': 'categorical_accuracy',
            'values': ['mean_absolute_error', acceptable_absolute_deviation],
        },
    }

    _default_callbacks = [
        ModelCheckpoint(KERAS_MODELS_FORMATTING),
        TerminateOnNaN(),
        EarlyStopping(monitor='loss', patience=3),
    ]

    def __getattr__(self, *args, **kwds):
        return self.model.__getattribute__(*args, **kwds)

    def __init__(
            self,
            num_items, num_users, num_item_features,
            num_neurons=100, dropout_chance=0.5,
    ):
        user_in, user_preferences, user_bias = _create_starting_layers(
            num_users,
            num_item_features,
            1,
            'user',
            l2(USER_REGULARIZATION_CONSTANT)
        )
        item_in, item_factors, item_bias = _create_starting_layers(
            num_items,
            num_item_features,
            2,
            'item',
            l2(ITEM_REGULARIZATION_CONSTANT)
        )

        simple_dot = dot([user_preferences, item_factors], axes=-1)
        simple_dot = add([simple_dot, user_bias, item_bias])
        simple_dot = Flatten()(simple_dot)
        aux_x = Dense(num_neurons, activation='relu', use_bias=True)(simple_dot)

        x = concatenate([
            Flatten()(user_preferences), user_bias,
            Flatten()(item_factors), item_bias,
        ])

        x = Dense(num_neurons, activation='relu', use_bias=True)(x)
        x = Dense(num_neurons, activation='relu', use_bias=True)(x)
        x = Dropout(dropout_chance)(x)
        x = Dense(num_neurons, activation=None, use_bias=True)(x)
        x = add([x, aux_x])
        x = Dense(num_neurons, activation='relu', use_bias=True)(x)
        x = Dense(num_neurons, activation='relu', use_bias=True)(x)
        x = Dropout(dropout_chance)(x)
        values = Dense(2, activation=None, name='values')(x)
        highest = Dense(2, activation='softmax', name='highest')(x)

        self.model = Model([item_in, user_in], [highest, values])

    def compile(self, **kwds):
        options = self._default_compile_parameters.copy()
        options.update(kwds)
        return self.model.compile(**options)

    def fit(
            self,
            x, y,
            batch_size=BATCH_SIZE,
            epochs=100,
            verbose=0,
            validation_split=0.1,
            **kwds
    ):
        callbacks = kwds.pop('callbacks', self._default_callbacks)
        return self.model.fit(
            x, y,
            batch_size=batch_size,
            epochs=epochs,
            verbose=verbose,
            callbacks=callbacks,
            validation_split=validation_split,
            **kwds
        )

    def fit_generator(self, epochs=100, verbose=0, **kwds):
        """A thin wrapper around keras.Model.fit_generator"""
        callbacks = kwds.pop('callbacks', self._default_callbacks)
        return self.model.fit_generator(
            epochs=epochs,
            verbose=verbose,
            callbacks=callbacks,
            workers=4,
            #AssertionError: daemonic processes are not allowed to have children
            use_multiprocessing=False,
            **kwds,
        )

    def train(self, ratings_df, games_id, validation_split=0.1, **kwds):
        batch_size = kwds.pop('batch_size', BATCH_SIZE)
        n_samples = ratings_df.shape[0]
        cutoff = int(-n_samples * validation_split)
        validation_df = ratings_df.iloc[cutoff:]
        training_df = ratings_df.iloc[:cutoff]
        training_generator = dp.BatchGenerator(training_df, games_id, batch_size)
        validation_generator = dp.BatchGenerator(validation_df, games_id, batch_size)
        return self.fit_generator(
            generator=training_generator,
            validation_data = validation_generator,
            **kwds
        )


class SingleUserModel(CollaborativeFilteringModel):
    def __init__(self, item_factors_layer_name='item_factors', player_id=None):
        self.model = load_model(
            PATH_TO_BEST_COLLABORATIVE_FILTERING_MODEL,
            custom_objects={
                'acceptable_absolute_deviation': acceptable_absolute_deviation,
            }
        )
        item_factors_layer = self.model.get_layer(item_factors_layer_name)
        item_factors_layer.trainable = False
        self.compile()
        self.player_id = player_id
        self._default_callbacks = [
            SaveBestToDatabase(player_id=self.player_id),
            TerminateOnNaN(),
            EarlyStopping(monitor='loss', patience=3),
        ]

    def fit(self, *args, **kwds):
        callbacks = kwds.pop('callbacks', self._default_callbacks)
        super().fit(*args, callbacks=callbacks, **kwds)
        return super().fit(*args, validation_split=0, callbacks=callbacks, **kwds)

    def train(self, ratings_df, games_id, **kwds):
        callbacks = kwds.pop('callbacks', self._default_callbacks)
        return super().train(ratings_df, games_id, callbacks=callbacks, **kwds)


class FindingSimilar(): pass
    # but does assume we know that object x is more similar to y than it is to z
