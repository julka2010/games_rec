from itertools import islice
import logging

from ijson import common
from ijson.backends import python as ijson_backend
import pandas as pd

from ratings.models import Game, Player, Rating

def floaten(event):
    if event[1] == 'number':
        return (event[0], event[1], float(event[2]))
    return event

def migrate_from_json_file_to_db(
        manager,
        json_file_path,
        to_model,
        chunk_size=4096
    ):
    """
    Moves data from json file to database.

    Params:
        - manager: Manager object for model you want to create
        - json_file_path: file to read from
        - to_model: callback function to transform loaded json to model
        - chunk_size: how many models to create at once
    """
    with open(json_file_path, 'r') as json_file:
        events = map(floaten, ijson_backend.parse(json_file))
        objects = common.items(events, 'item')
        chunks = chunk(objects, chunk_size)
        for c in chunks:
            models = []
            for obj in c:
                model = to_model(obj)
                if model is not None:
                    models.append(model)
            manager.bulk_create(models)


def migrate_ratings_file(json_file_path):
    games = Game.objects.all()
    games = pd.DataFrame.from_records(games.values('bgg_id', 'id'))
    games = games.set_index('bgg_id')
    players = Player.objects.all()
    players = pd.DataFrame.from_records(players.values())
    players = players.set_index('bgg_username')
    migrate_from_json_file_to_db(
        Rating.objects,
        json_file_path,
        lambda x: to_rating(x, games, players)
    )


def to_rating(obj, games, players):
    try:
        bgg_game_id = int(obj['game_id'])
        username = obj['username']
        r = {
            'value': obj['rating'],
            'game_id': games.loc[bgg_game_id].id,
            'player_id': players.loc[username].id,
        }
    except KeyError as e:
        if bgg_game_id not in games.index:
            new_game = Game(bgg_id=bgg_game_id)
            new_game.save()
            print(
                "Created a new empty game with bgg_id {bgg_game_id}, "
                "pk {new_game.pk}".format(**locals())
            )
            games.loc[bgg_game_id] = new_game.pk
            return to_rating(obj, games, players)
        else:
            print("Player {u} not found in database".format(u=username))
        return None
    if r['value'] is None:
        return None
    return Rating(**r)

def to_game(obj):
    obj['bgg_id'] = obj.pop('game_id')
    return Game(**obj)


_no_padding = object()  # pylint: disable=invalid-name
def chunk(it, size, padval=_no_padding):
    """
    Splits iterable into defined-size chunks.

    Copy pasted sendele's code from https://stackoverflow.com/a/22045226
    """
    it = iter(it)
    chunker = iter(lambda: tuple(islice(it, size)), ())
    if padval == _no_padding:
        yield from chunker
    else:
        for ch in chunker:
            yield ch if len(ch) == size else ch + (padval,) * (size - len(ch))
