from __future__ import absolute_import

from celery import shared_task
import pandas as pd
import numpy as np

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
    history = model.fit(
        {
            'user_in': ratings.player_id.values,
            'item_in': ratings.game_id.values,
        },
        [ratings.value.values, ratings.value.values],
        verbose=1,
    )
    return history, model


@shared_task
def train_player(player):
    qs = player.rating_set.all()
    ratings = pd.DataFrame.from_records(qs.values())
    ratings = data_preparation.to_keras_model_indices(ratings)
    np.random.shuffle(ratings.values)
    model = training.keras.models.SingleUserModel()
    history = model.fit(
        {
            'user_in': ratings.player_id.values,
            'item_in': ratings.game_id.values
        },
        [ratings.value.values, ratings.value.values],
        verbose=1
    )
    return history, model
