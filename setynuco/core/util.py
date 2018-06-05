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
            if '.' in c or c.isdigit():
                try:
                    clean_column.append(float(c))
                except Exception as e:
                    pass
    return clean_column


# The below code is used to test the performance of get_numericals function
# import timeit
#
# statements=["""\
# try:
#     b = float(a)
# except Exception as e:
#     pass""",
# # """\
# # if '.' in a:
# #     l = a.split('.')
# #     if len(l) == 2:
# #         if l[0].isdigit() and l[1].isdigit():
# #             b = float(a)""",
# """\
# if '.' in a or a.isdigit():
#     try:
#         b = float(a)
#     except Exception as e:
#          pass"""]
#
# for a in ("11", "12.5", "abc", "a.3"):
#     for s in statements:
#         # t = timeit.Timer(stmt=s, setup='a={}'.format(a))
#         t = timeit.Timer(stmt=s, setup='a="%s"' % str(a))
#         print("a = {}\n{}".format(a,s))
#         print("%.2f usec/pass\n" % (1000000 * t.timeit(number=100000)/100000))
