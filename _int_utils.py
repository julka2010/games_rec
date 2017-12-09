from importlib import reload
from pprint import pprint
import random

import numpy as np

import recommender
import utils

doc_ids = [int(t) for t in 
    ['13', '18', '34', '188', '249', '432', '438', '478', '712', '822', '903', '1465', '1927', '2651', '2944', '3076', '6249', '8098', '9209', '9220', '10547', '12942', '13592', '19237', '21882', '22545', '28143', '30549', '36218', '37111', '38453', '39856', '40692', '40816', '41757', '58110', '63268', '65673', '68448', '72125', '84876', '97207', '98085', '98778', '100423', '100679', '103343', '104581', '108745', '113636', '120677', '121921', '122515', '124742', '126163', '128882', '143515', '147116', '147949', '148228', '148949', '158392', '161970', '162007', '167400', '170216', '172225', '176189', '176396', '176494', '178900', '181304', '181530', '181796', '188834', '193738', '202408']
]

r, rg, tg, lg, mg, ru, tu, lu, mu, indices, values, shape, gmean = (
    utils._setup_for_interactive(
        '/home/julka/LP/games_rec/scrap_bgg/games_sorted.csv')
    )


def iter_val(user, step=1, want_preds=False):
    val_diff = []
    preds = []
    for s in range(0, len(user[0]), step):
        pred, diff = recommender.predict(
            (user[0][:s]+user[0][s+step:],user[1][:s]+user[1][s+step:],user[2]),
            mg, gmean,
            (user[0][s:s+step], user[1][s:s+step], user[2])
        )
        val_diff.append(diff ** 0.5)
        preds.append(pred[user[0][s][0]])
    if want_preds:
        return val_diff, preds
    else:
        return val_diff


def pred_wrong(user, correct_rating_threshold=1):
    val_diff, preds = np.array(iter_val(user, want_preds=True))
    wrong_pred = val_diff > correct_rating_threshold
    wrong_predictions = []

    for i, val in enumerate(wrong_pred):
        if val:
            wrong_predictions.append(
                [lg[user[0][i][0]], val_diff[i], user[1][i], preds[i]])
    return wrong_predictions


def pred(user):
    return recommender.predict(user, mg, gmean)[0]


def user(user_string, delim='\n'):
    user = [[], [], []] #indices, values, shape
    values = user_string.split(delim)
    for i, game_id in enumerate(doc_ids):
        print('{:>6} - {}'.format(game_id, values[i]))
        if values[i] is not '':
            user[0].append([tg[game_id], 0])
            user[1].append(float(values[i]))
    user[2] = len(lg), 1
    return user


def val_suggest(user, step=1, top=10):
    val_diff = iter_val(user, step)
    user_pred = pred(user)
    suggest = utils.suggest(
        user_pred,
        lambda x: utils.filter_by_num_ratings(x, rg),
        lg,
        top
    )
    print((np.median(val_diff), np.mean(val_diff), max(val_diff)))
    return [utils._bgg_link(t) for t in suggest]
