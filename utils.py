import csv
import itertools
import random

import numpy as np

def read_user_list_file(file_):
    ratings = []
    with open(file_, 'r') as csvfile:
        reader = csv.reader(csvfile, dialect='unix')
        for row in reader:
            ratings.append(row)
    return ratings

def group_ratings_by_key(ratings, key):
    ratings_grouped = {}
    ratings = sorted(ratings, key=lambda x: x[key])
    for grouper, group in itertools.groupby(ratings, lambda x: x[key]):
        list_ = [itertools.chain(x[:key] + x[key+1:]) for x in group]
        ratings_grouped[grouper] = dict(list_)
    return ratings_grouped

def index(dict_):
    index = {}
    for i, k in enumerate(dict_):
        index[k] = i
    return index

def ratings_indices(ratings):
    coords = []
    values = []
    for rating in ratings:
        coords.append([rating[0], rating[1]])
        values.append(rating[2])
    return (coords, values)

def _setup_for_interactive(userfile):
    def _set_of_variables(key):
        grouped = group_ratings_by_key(ratings, key)
        table = index(grouped)
        list_ = [k for k in table.keys()]
        return grouped, table, list_
    def calculate_mean_ratings(grouped_ratings):
        means = []
        for pair in grouped_ratings.values():
            means.append([np.mean([r for r in pair.values()]) - global_mean])
        return np.array(means)
    ratings = read_user_list_file(userfile)
    temp_ratings = []  #ignore any rows without rating
    for r in ratings:
        if len(r[2]) > 0:
            temp_ratings.append([int(float(r[0])), r[1], float(r[2])])
    ratings = temp_ratings
    del temp_ratings
    ratings_by_game, table_games, list_games = _set_of_variables(0)
    ratings_by_user, table_users, list_users = _set_of_variables(1)
    ratings_indexed = [
        [table_games[t[0]], table_users[t[1]], t[2]] for t in ratings]
    indices, values = ratings_indices(ratings_indexed)
    shape = np.array([len(list_games), len(list_users)])
    global_mean = np.mean(values)
    means_game = calculate_mean_ratings(ratings_by_game)
    means_user = calculate_mean_ratings(ratings_by_user)
    return (
        ratings,
        ratings_by_game, table_games, list_games, means_game,
        ratings_by_user, table_users, list_users, means_user,
        indices, values, shape,
        global_mean,
    )
