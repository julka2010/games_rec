import os

SUBDIRECTORY_FOR_SAVING_MODELS = 'saved_models'
PATH_TO_BEST_COLLABORATIVE_FILTERING_MODEL = os.path.join(
    SUBDIRECTORY_FOR_SAVING_MODELS,
    'model-010-3.56.hdf5',
)
MODEL_CHECKPOINT_STRING = os.path.join(
    SUBDIRECTORY_FOR_SAVING_MODELS,
    'model-{epoch:03d}-{val_loss:.2f}.hdf5'
)
