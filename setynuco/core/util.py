import features
import numpy as np


def round_acc(x):
    return round(x, 2)


def strip_uri(uri):
    if uri[0] == "<":
        return uri[1:len(uri)-1]
    return uri


def remove_outliers(column):
    """
    :param column: list of numbers
    :return:
    """
    clean_column = []
    q1 = features.q1(column)
    q3 = features.q3(column)
    k = 1.5
    # [Q1 - k(Q3 - Q1), Q3 + k(Q3 - Q1)]
    lower_bound = q1 - k*(q3-q1)
    upper_bound = q3 + k*(q3-q1)
    for c in column:
        if c >= lower_bound and c <= upper_bound:
            clean_column.append(c)
    return column


def get_numericals(column):
    """
    :param column:
    :return: list of numeric values
    """
    clean_column = []
    for c in column:
        if isinstance(c, (int, float)):
            if not np.isnan(c):
                clean_column.append(c)
        elif isinstance(c, basestring):
            if c.isdigit():
                clean_column.append(float(c))
    return clean_column
