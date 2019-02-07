from __future__ import absolute_import
from functools import cmp_to_key
import logging

from celery import  shared_task
import numpy as np
import pandas as pd

from ratings.models import Player
from training.models import KerasSinglePlayerModel, TrainedOnGame
import training.keras.models
import training.keras.data_preparation as dp

from training.keras.utils.constants import NUM_ITEM_FEATURES

@shared_task
def train_everything(rebuild_indices=True):
    ratings = dp.load_dataset()
    ratings = dp.to_keras_model_indices(
        ratings, rebuild_indices=rebuild_indices
    )
    np.random.shuffle(ratings.values)
    model = training.keras.models.CollaborativeFilteringModel(
        max(ratings.game_id) + 1,
        max(ratings.player_id) + 1,
        NUM_ITEM_FEATURES,
    )
    model.compile()
    _history = model.train(
        ratings,
        ratings.game_id.unique(),
        verbose=1,
    )


@shared_task
def train_player(player_id):
    player = Player.objects.get(pk=player_id)
    qs = player.rating_set.all()
    ratings = pd.DataFrame.from_records(qs.values())
    ratings = dp.to_keras_model_indices(ratings)
    np.random.shuffle(ratings.values)
    model = training.keras.models.SingleUserModel(
        player_id=player_id,
    )
    _history = model.train(
        ratings,
        TrainedOnGame.objects.all().values_list('pk', flat=True),
        verbose=2,
    )


@shared_task
def get_player_predictions(model_id, games_id, limit):
    def _compare_two_games(a, b):
        inputs = {
            'user_in': player_indice,
            'item_in': np.array((a, b)).reshape(-1, 2),
        }
        values, highest = model.keras_model.predict(inputs)
        highest = np.squeeze(highest)
        return highest[0] - highest[1]

    model = KerasSinglePlayerModel.objects.get(id=model_id)
    to_be_pred = pd.DataFrame(games_id, columns=['game_id'])
    del games_id
    to_be_pred['player_id'] = model.player_id  # pylint: disable=no-member
    logging.info(
        "Getting predictions for player %d via model %s %d",
        model.player_id,
        type(model),
        model_id
    )
    logging.debug("Head of DataFrame to be processed:\n%s", to_be_pred.head())
    to_be_pred = dp.to_keras_model_indices(to_be_pred)
    player_indice = to_be_pred.player_id
    recommendations = pd.DataFrame(sorted(
        to_be_pred.game_id,
        key=cmp_to_key(_compare_two_games),
    )[:limit], columns=['model_game_id'])
    logging.error(recommendations)
    return dp.to_pks(recommendations).to_json()
