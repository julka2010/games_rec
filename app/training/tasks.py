from __future__ import absolute_import

from celery import  shared_task
import numpy as np
import pandas as pd

from ratings.models import Player
from training.models import KerasSinglePlayerModel
import training.keras.models
from training.keras import (
    data_preparation,
)
from training.keras.utils.constants import NUM_ITEM_FEATURES

@shared_task
def train_everything(rebuild_indices=True):
    ratings = data_preparation.load_dataset()
    ratings = data_preparation.to_keras_model_indices(
        ratings, rebuild_indices=rebuild_indices
    )
    np.random.shuffle(ratings.values)
    model = training.keras.models.CollaborativeFilteringModel(
        max(ratings.game_id) + 1,
        max(ratings.player_id) + 1,
        NUM_ITEM_FEATURES,
    )
    model.compile()
    _history = model.fit(
        {
            'user_in': ratings.player_id.values,
            'item_in': ratings.game_id.values,
        },
        [ratings.value.values, ratings.value.values],
        verbose=1,
    )


@shared_task
def train_player(player_id):
    player = Player.objects.get(pk=player_id)
    qs = player.rating_set.all()
    ratings = pd.DataFrame.from_records(qs.values())
    ratings = data_preparation.to_keras_model_indices(ratings)
    np.random.shuffle(ratings.values)
    model = training.keras.models.SingleUserModel(
        player_id=player_id,
    )
    _history = model.fit(
        {
            'user_in': ratings.player_id.values,
            'item_in': ratings.game_id.values
        },
        [ratings.value.values, ratings.value.values],
        verbose=2
    )


@shared_task
def get_player_predictions(model_id, games_id, limit):
    model = KerasSinglePlayerModel.objects.get(id=model_id)
    to_be_pred = pd.read_json(games_id)
    to_be_pred['player_id'] = model.player_id  # pylint: disable=no-member
    to_be_pred = data_preparation.to_keras_model_indices(to_be_pred)
    ratings, _ = model.keras_model.predict( # pylint: disable=no-member
        {
            'user_in': to_be_pred.player_id.values,
            'item_in': to_be_pred.game_id.values,
        },
    )
    recommendations = pd.DataFrame({
            'prediction': ratings.reshape(-1),
            'model_game_id': to_be_pred.game_id.values
    }).sort_values('prediction', ascending=False).reset_index(drop=True)
    recommendations = recommendations.iloc[:limit]
    return recommendations.to_json()
