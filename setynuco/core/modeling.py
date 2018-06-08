#################################################################
#                        Modeling                               #
#################################################################
from djangomodels import *
from setynuco.models import *
import util
import logging
import numpy as np


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def model_add(name, knowledge_graph, class_uris):
    mlmodel = MLModel()
    mlmodel.name = name
    mlmodel.knowledge_graph = knowledge_graph
    mlmodel.save()
    logger.info(class_uris)
    for curi in class_uris:
        logger.debug("will add <%s>" % curi)
        ModelClass(model=mlmodel, class_uri=curi).save()
    return mlmodel


def add_cluster_to_model(model, name, features):
    Cluster(model=model, name=name, center=",".join(str(util.round_acc(f)) for f in features)).save()


def update_model_progress_for_partial(model, new_progress):
    return update_model_state(model=model, new_progress=new_progress)


def update_model_state(model, new_state=None, new_notes=None, new_progress=None):
    if new_state is not None:
        model.status = new_state
    if new_notes is not None:
        model.notes = new_notes
    if new_progress is not None:
        model.progress = new_progress
    model.save()
    return model


def merge_clusters(model):
    properties = []
    for clus in model.cluster_set.all():
        class_name, property_name = clus.name.split(' ')
        properties.append(property_name)
    properties = list(set(properties))
    for property in properties:
        clusters_models = model.cluster_set.filter(name__endswith=property)
        clusters = [np.array(util.get_numericals(clus_model.center.split(','))) for clus_model in clusters_models]
        clusters_np = np.array(clusters)
        print "clusters np:"
        print clusters_np
        clus_avg = np.average(clusters_np, axis=0)
        clus_avg_str = ",".join(str(util.round_acc(x)) for x in clus_avg)
        new_clus = Cluster(name=property, center=clus_avg_str, model=model)
        new_clus.save()
        for clus_model in clusters_models:
            clus_model.delete()
