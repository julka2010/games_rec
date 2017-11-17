import csv
import itertools

def read_user_list_file(file_):
    ratings = []
    with open(file_, 'r') as csvfile:
        reader = csv.reader(csvfile, dialect='unix')
        for row in reader:
            ratings.append(row)
    return ratings[1:]  #Assume header row

def group_ratings_by_key(ratings, key):
    ratings_grouped = {}
    ratings = sorted(ratings, key=lambda x: x[key])
    for grouper, group in itertools.groupby(ratings, lambda x: x[key]):
        list_ = [itertools.chain(x[:key] + x[key+1:]) for x in group]
        ratings_grouped[grouper] = dict(list_)
    return ratings_grouped
