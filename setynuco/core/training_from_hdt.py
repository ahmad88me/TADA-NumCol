import os
from hdt import HDTDocument
from setynuco.settings import HDT_DIR

import logging
from logger import set_config
logger = set_config(logging.getLogger(__name__))


def load_hdt(file_name):
    # Load HDT file. Missing indexes are generated automatically
    document = HDTDocument(file_name)
    return document


def get_classes(document):
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
            f.write('%s\n', c.strip())
        f.close()


def write_classes_if_needed(document):
    out_file_dir = os.path.join(HDT_DIR, 'classes.csv')
    if not os.path.isfile(out_file_dir):
        classes = get_classes(document)
        write_classes(classes)


def workflow(file_dir):
    document = load_hdt(file_dir)
    write_classes_if_needed(document)

