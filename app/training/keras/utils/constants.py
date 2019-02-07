import os

from game_recommendations.settings import MEDIA_ROOT

KERAS_MODELS_DIR = ('keras_models')
ABSOLUTE_KERAS_MODELS_DIR = os.path.join(MEDIA_ROOT, KERAS_MODELS_DIR)
KERAS_MODELS_FORMATTING = os.path.join(
    ABSOLUTE_KERAS_MODELS_DIR, 'weights.{epoch:02d}-{val_loss:.2f}.hdf5'
)

NUM_ITEM_FEATURES = 50
MIN_RATINGS_FOR_TRAINING = 10

BATCH_SIZE = 2**10

ITEM_REGULARIZATION_CONSTANT = 10e-4
USER_REGULARIZATION_CONSTANT = 10e-5

PATH_TO_BEST_COLLABORATIVE_FILTERING_MODEL = os.path.join(
    ABSOLUTE_KERAS_MODELS_DIR, 'weights.09-0.00.hdf5'
)
