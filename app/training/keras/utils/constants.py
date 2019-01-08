import os

KERAS_MODELS_DIR = os.path.join('/var', 'lib', 'keras_models')
KERAS_MODELS_FORMATTING = os.path.join(
    KERAS_MODELS_DIR, 'weights.{epoch:02d}-{val_loss:.2f}.hdf5'
)

NUM_ITEM_FEATURES = 50
MIN_RATINGS_FOR_TRAINING = 10

BATCH_SIZE = 2**10
