# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


import pandas as pd
import numpy as np
from multiprocessing import Process, Lock
import features
import os
from config import ROUNDING, min_num_of_objects
from setynuco.settings import UPLOAD_DIR


def create_model(file_dir):
    out_file_dir = os.path.join(UPLOAD_DIR, "models.csv")
    f = open(out_file_dir, "w")
    f.close()
    print "input: %s" % file_dir
    print "output: %s" % out_file_dir
    file_lock = Lock()
    processes = []
    df = pd.read_csv(file_dir, header=None)
    num_of_spawned = 0
    prev_class_name = prev_property = class_name = property = ""
    for index, row in df.iterrows():
        prev_class_name = row[0]
        prev_property = row[1]
        ff = open(out_file_dir, 'w')
        ff.write("class, property, mean, median, std\n")
        ff.close()
        break

    print "prev: "
    print prev_class_name
    print prev_property
    num_values = []
    for index, row in df.iterrows():
        class_name = row[0]
        property = row[1]
        num_val = row[2]
        if class_name != prev_class_name or prev_property != property:  # new class property combination started
            print prev_class_name
            print class_name
            print property
            print prev_property
            print "in the if"
            if len(num_values) >= min_num_of_objects:
                print "more than min"
                num_of_spawned += 1
                print "process: "
                print property
                p = Process(target=store_features, args=(out_file_dir, prev_class_name, prev_property, num_values, file_lock))
                p.start()
                processes.append(p)
            else:
                print "instead only have: "
                print len(num_values)
            prev_class_name = class_name
            prev_property = property
            num_values = [float(num_val)]
        else:
            num_values.append(float(num_val))
    if len(num_values) >= min_num_of_objects:
        num_of_spawned += 1
        p = Process(target=store_features, args=(out_file_dir, class_name, property, num_values, file_lock))
        p.start()
        processes.append(p)

    # wait for the processes to finish their work
    for idx, p in enumerate(processes):
        print("#spawned: %d, #finished: %d" % (num_of_spawned, idx+1))
        p.join()
    print("")


def store_features(file_dir, class_name, property_uri, values, lock):
    """
    Compute and store the features in the given file
    :param file_dir: dir of the output file
    :param class_name: semantic type
    :param property: semantic property
    :param values: list of numerical values for the given class,property pair
    :param lock: for the file, so we can run it multiple processes
    :return:
    """
    features_values = features.compute_curr_features(np.array(values))
    # compute features
    # features_values = [1, 2, 3]
    lock.acquire()
    ff = open(file_dir, 'a')
    ff.write('''"%s","%s",%s\n''' % (class_name, property_uri, ",".join([str(round(f, ROUNDING)) for f in features_values])))
    ff.close()
    lock.release()
