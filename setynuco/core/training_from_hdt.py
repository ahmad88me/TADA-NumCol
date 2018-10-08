# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


import os
from hdt import HDTDocument
from setynuco.settings import HDT_DIR
from PPool.Pool import Pool
from multiprocessing import Lock
from collections import Counter
from config import min_num_of_entities_per_property, min_num_of_objects
import features
import util
from training_from_file import store_features
import numpy as np
import logging
from logger import set_config
logger = set_config(logging.getLogger(__name__))

NUM_OF_PROCESSES = 1


def load_hdt(file_name):
    # Load HDT file. Missing indexes are generated automatically
    document = HDTDocument(file_name)
    return document


def get_classes_from_hdt(document):
    """
    :param document: HDTDocument
    :return: set of classes
    """
    (triples, cardinality) = document.search_triples("", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "")
    classes = set()
    for _, _, c in triples:
        classes.add(c)
    return classes


def write_classes(classes, out_file_dir):
        f = open(out_file_dir,'w')
        for c in classes:
            f.write('%s\n'% c.strip())
        f.close()


def get_and_write_classes(out_file_dir, leaves_file_dir, document):
    if not os.path.isfile(out_file_dir) and not os.path.isfile(leaves_file_dir):
        classes = get_classes_from_hdt(document)
        write_classes(classes, out_file_dir)
    return get_classes_from_file(out_file_dir)


def get_classes_from_file(classes_file_dir):
    """
    :param classes_file_dir: the dir of the file that includes the list of all classes
    :return: list of classes
    """
    f = open(classes_file_dir)
    classes = []
    for c in f.readlines():
        classes.append(c.strip())
    #logger.info("we got %d classes: " % len(classes))
    return classes

# def write_top_k(document, in_file_dir, out_file_dir, k):
#     f = open(in_file_dir)
#     classes = [] # because the input file should not have duplicates
#     for line in f.readline():
#         (_, cardinality) = document.search_triples("", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", line)
#         if cardinality >= k:
#             classes.append(line)
#     f.close()
#
#     f = open(out_file_dir, 'w')
#     for c in classes:
#         f.write()


def build_model_for_class_property(class_uri, property_uri, out_file_dir, lock, document):
    (triples, cardinality) = document.search_triples("", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", class_uri)
    objects = []
    for s, _, _ in triples:
        (triples2, cardinality) = document.search_triples(s, property_uri, "")
        for _, _, o in triples2:
            objects.append(o)

    if len(objects) >= min_num_of_objects:
        #logger.info("min num of objects 1 passed")
        nums = util.get_numericals(objects)
        if len(nums) >= min_num_of_objects:
            logger.info("build_model_for_class_property> %20s   |   %20s "% (class_uri, property_uri))
            store_features(file_dir=out_file_dir, class_name=class_uri, property_uri=property_uri, values=nums, lock=lock)
        # else:
        #     logger.info("min num of objects 2 NOT: %d"%len(nums))
    # else:
    #     logger.info("min num of objects 1 NOT")


# def build_model_for_class_property(class_uri, property_uri, out_file_dir, lock, document):
#     (triples, cardinality) = document.search_triples(class_uri, property_uri, "")
#     if cardinality >= min_num_of_objects:
#         objects = [v[2] for v in triples]
#         nums = util.get_numericals(objects)
#         if len(nums) >= min_num_of_objects:
#             logger.info("build_model_for_class_property> %20s   |   %20s "% (class_uri, property_uri))
#             store_features(file_dir=out_file_dir, class_name=class_uri, property_uri=property_uri, values=nums, lock=lock)


def append_to_model_func(class_uri, out_file_dir, lock, document):
    #document = load_hdt(hdt_dir)
    #print("nb triples: %i" % document.total_triples)
    properties = get_properties_for_class(class_uri, document)
    #logger.info("append_to_model_func> class:  %s" % class_uri)
    for p in properties:
        #logger.info("append_to_model_func> %20s,%20s" % (class_uri[:20], p[:20]))
        build_model_for_class_property(class_uri, p, out_file_dir, lock, document)


def build_model(classes, out_file_dir, document):
    print("outfile file: "+out_file_dir)
    params = []
    lock = Lock()
    for c in classes:
        params.append((c, out_file_dir, lock, document))
    pool = Pool(max_num_of_processes=NUM_OF_PROCESSES, func=append_to_model_func, params_list=params, logger=logger)
    pool.run()
    # for testing
    # print("params [0]: ")
    # print(params[0])
    # append_to_model_func(*params[0])


def get_properties_for_class(class_uri, document):
    (triples, ccardinality) = document.search_triples("", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", class_uri)
    logger.info("subject cardinality of <%s>: %d" % (class_uri, ccardinality))
    property_counter = {}  # this is not unique, so we can use a counter after to see the occurences of each property
    idx = 0
    step_size = ccardinality/100
    if step_size == 0:
        step_size = ccardinality
    logger.info("step size <%s>: %d" % (class_uri, step_size))
    for s, _, _ in triples:
        if idx % step_size == 0:
            logger.info("get_properties_for_class> %s    (%d %%)" % (class_uri, idx*100/ccardinality))
        idx += 1
        (triples2, cardinality) = document.search_triples(s, "", "")
        for _, p, _ in triples2:
            if p not in property_counter.keys():
                property_counter[p] = 1
            else:
                property_counter[p] += 1
    picked_properties = []
    ccardinality = len(property_counter.keys())
    #logger.info("get_properties_for_class> %s keys: %d " % (class_uri, ccardinality))
    # step_size = ccardinality/100
    # if step_size == 0:
    #     step_size = ccardinality
    # idx = 0
    for k in property_counter.keys():
        # if idx % step_size == 0:
        #     logger.info("get_properties_for_class> %s keys (%d %%)" % (class_uri, idx * 100 / ccardinality))
        # idx += 1
        occurences = property_counter[k]
        if occurences >= min_num_of_entities_per_property:
            picked_properties.append(k)
    logger.info("%s picked properties: %d" % (class_uri, len(picked_properties)))
    return picked_properties


def append_class_property_func(class_uri, out_file_dir, lock, document):
    logger.info("getting properties for: %s" % class_uri)
    properties = get_properties_for_class(class_uri, document)
    logger.info("got %d properties for %s" % (len(properties), class_uri))
    s = class_uri + "\t"
    s += "\t".join(properties)
    s += "\n"
    lock.acquire()
    f = open(out_file_dir, "a")
    f.write(s)
    f.close()
    lock.release()


def build_class_property(classes, out_file_dir, num_file_dir, document, resume):
    """
    This function is responsible of writing a TSV file (Tab Separated Values)
    with the first element as the class uri and the rest are the properties.
    :param classes: list of classes
    :param out_file_dir:
    :param document:
    :return: Nothing
    """
    params = []
    lock = Lock()
    classes_to_process = classes
    if resume and os.path.isfile(out_file_dir):
        processed_classes = []
        f = open(out_file_dir)
        for line in f.readlines():
            if line.strip() != '':
                class_uri = line.split('\t')[0]
                processed_classes.append(class_uri)
        classes_to_process = list(set(classes) - set(processed_classes))
        print("missed classes to process: %d" % (len(classes_to_process)))
    # If out file does not exists and numerical out file does not exists OR
    # if resume is intended and the out file does exists
    if (not os.path.isfile(out_file_dir) and not os.path.isfile(num_file_dir)) or (resume and os.path.isfile(out_file_dir)):
        for c in classes_to_process:
            params.append((c, out_file_dir, lock, document))
        pool = Pool(max_num_of_processes=NUM_OF_PROCESSES, func=append_class_property_func, params_list=params, logger=logger)
        pool.run()


def get_leaves_classes_from_file(out_file_dir):
    leaves = []
    f = open(out_file_dir)
    for line in f.readlines():
        leaves.append(line.strip())
    return leaves


def get_and_write_leaves_classes(classes, out_file_dir, document):
    leaves = []
    if not os.path.isfile(out_file_dir):
        for c in classes:
            (triples, cardinality) = document.search_triples("", "http://www.w3.org/2000/01/rdf-schema#subClassOf", c)
            if cardinality == 0:
                print("leaf: <%s>" % c)
                leaves.append(c)
        f = open(out_file_dir, "a")
        for leaf in leaves:
            f.write("%s\n" % leaf)
        f.close()
        return leaves
    else:
        return get_leaves_classes_from_file(out_file_dir)


def workflow(file_dir):
    classes_dir = os.path.join(HDT_DIR, 'classes_all.csv')
    leaves_classes_dir = os.path.join(HDT_DIR, 'leaves_classes.csv')
    class_property_dir = os.path.join(HDT_DIR, 'class_property_all.tsv')
    class_property_num_dir = os.path.join(HDT_DIR, 'class_property_num.tsv')
    model_dir = os.path.join(HDT_DIR, 'model.csv')
    document = load_hdt(file_dir)
    if document:
        classes = get_and_write_classes(classes_dir, leaves_classes_dir, document)
        leave_classes = get_and_write_leaves_classes(classes, leaves_classes_dir, document)
        build_class_property(classes=leave_classes, out_file_dir=class_property_dir, num_file_dir=class_property_num_dir,
                              document=document, resume=True)
        # build_class_numerical_property(classes=classes)
        # build_model(classes=classes, out_file_dir=os.path.join(HDT_DIR, 'model.csv'), document=document)
        #build_model(classes=classes, out_file_dir=os.path.join(HDT_DIR, 'model.csv'), hdt_dir=file_dir)