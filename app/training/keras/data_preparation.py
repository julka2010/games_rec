from django.db.models import Count
from keras.utils import Sequence, to_categorical
import numpy as np
import pandas as pd

from ratings.models import Game, Player, Rating
from training.keras.utils.constants import (
    MIN_RATINGS_FOR_TRAINING,
)
from training.models import TrainedOnGame, TrainedOnPlayer
from training.keras.utils.constants import BATCH_SIZE

def _filter_by_sufficient_no_ratings(df):
    def _filter(key):
        counts = df[key].value_counts()
        ids = set(counts[counts >= MIN_RATINGS_FOR_TRAINING].index)
        return df[df[key].isin(ids)]
    df = _filter('player_id')
    df = _filter('game_id')
    return df.reset_index(drop=True)


def _to_trained_on(df, key, ModelClass, rebuild):
    ids = pd.Series(df[key].unique())
    if rebuild:
        ModelClass.objects.all().delete()
        trained_on = []
        for i, id_ in enumerate(ids):
            kwds = {'id_in_model': i, key: id_}
            trained_on.append(ModelClass(**kwds))
        ModelClass.objects.bulk_create(trained_on)
        id_to_model_indice = pd.Series(ids.index, index=ids)
    else:
        kwds = {'{}__in'.format(key): ids}
        trained_on = ModelClass.objects.all().filter(**kwds)
        trained_on_df = pd.DataFrame.from_records(trained_on.values())
        trained_on_df = trained_on_df.set_index(key)
        id_to_model_indice = pd.Series(
            trained_on_df.id_in_model, index=trained_on_df.index
        )

    df.loc[:, key] = df[key].map(id_to_model_indice)
    df = df.dropna()
    return df


def load_dataset():
    qs = Rating.objects.all()
    df = pd.DataFrame.from_records(qs.values()).dropna()
    df = _filter_by_sufficient_no_ratings(df)
    return df


def to_keras_model_indices(df, rebuild_indices=False):
    df = _to_trained_on(df, 'game_id', TrainedOnGame, rebuild=rebuild_indices)
    df = _to_trained_on(df, 'player_id', TrainedOnPlayer, rebuild=rebuild_indices)
    return df


class BatchGenerator(Sequence):
    def __init__(
        self,
        ratings_df,
        games_id,
        batch_size=BATCH_SIZE,
        unplayed_split=0,
        shuffle=True
    ):
        self.ratings_df = ratings_df
        self.ratings_by_player = ratings_df.groupby('player_id')
        self.games_id = games_id
        self.batch_size = batch_size
        if not shuffle:
            raise RuntimeError('Values will be shuffled.')
        self.shuffle = shuffle
        self.on_epoch_end()

    def __data_generation(self, temp_indexes):
        temp_ratings = self.original.iloc[temp_indexes]
        players_id = temp_ratings.player_id
        second_games = self.comparison.iloc[temp_indexes]
        games_id = np.column_stack((temp_ratings.game_id, second_games.game_id))
        values = np.column_stack((temp_ratings.value, second_games.value))
        highest = to_categorical(values.argmax(axis=-1), num_classes=2)
        inputs = {'user_in': players_id, 'item_in': games_id}
        outputs = {'values': values, 'highest': highest}
        return inputs, outputs

    def __getitem__(self, index):
        indexes = np.arange(self.batch_size) + self.batch_size * index
        inputs, outputs = self.__data_generation(self.indexes[indexes])
        return inputs, outputs

    def __len__(self):
        """Number of batches per epoch."""
        return int(np.floor(self.ratings_df.shape[0] / self.batch_size))

    def on_epoch_end(self):
        """Updates indexes after after each epoch."""
        def shuffle_by_player():
            df = self.ratings_player.apply(lambda x: x.sample(frac=1))
            return df.reset_index(drop=True)
        self.original = shuffle_by_player()
        self.comparison = shuffle_by_player()
        self.indexes = np.arange(self.ratings_df.shape[0])
        if self.shuffle:
            np.random.shuffle(self.indexes)


# =============================================================================
# From data keras works on to data db works on ================================
# =============================================================================

def to_pks(df):
    trained_on_games = TrainedOnGame.objects.all().filter(
        pk__in=df.model_game_id)
    trained_on_df = pd.DataFrame.from_records(
        trained_on_games.values('pk', 'game'))
    trained_on = pd.Series(trained_on_df.set_index('pk')['game'])

    df['pk'] = df.model_game_id.map(trained_on)
    return df


def to_board_game_geek_ids(df):
    df = to_pks(df)
    trained_on_bgg_games = Game.objects.filter(pk__in=trained_on_df.game)
    trained_on_bgg_games = pd.DataFrame.from_records(
        trained_on_bgg_games.values('pk', 'bgg_id'))
    trained_on_bgg_games = pd.Series(trained_on_bgg_games.set_index('pk')['bgg_id'])

    df['bgg_id'] = df['pk'].map(trained_on_bgg_games)
    return df
