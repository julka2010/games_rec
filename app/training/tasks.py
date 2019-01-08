from __future__ import absolute_import
from celery import shared_task

import training.keras.models
from training.keras import (
    data_preparation,
)
from training.keras.utils.constants import NUM_ITEM_FEATURES

@shared_task
def add(x, y):
    return x + y

@shared_task
def train_everything():
    ratings = data_preparation.load_dataset()
    ratings = data_preparation.to_keras_model_indices(ratings)
    model = training.keras.models.CollaborativeFiltering(
        max(ratings.game_id) + 1,
        max(ratings.player_id) + 1,
        NUM_ITEM_FEATURES,
    )
    numpy_rating_values = ratings.value.values / 10.0
    model.compile()
    try:
        model.fit(
            {
                'user_in': ratings.player_id.values,
                'item_in': ratings.game_id.values,
            },
            [numpy_rating_values, numpy_rating_values],
            verbose=1,
        )
    except Exception: pass
    return model
