import numpy as np
from fuzzycmeans import FCM
from djangomodels import *


def compute_features(column, ffuncs):
    feature_vector = []
    for ff in ffuncs:
        feature_vector.append(ff(column))
    #return np.array(feature_vector)
    return feature_vector


def mean(column):
    return np.average(column)


def variance(column):
    return np.var(column)


def std(column):
    return np.std(column)


def q1(column):
    # return np.percentile(column, 25)
    # print("the column: ")
    # print(column)
    return np.percentile(column, 25)


def q3(column):
    # return np.percentile(column, 75)
    return np.percentile(np.array(column), 75)