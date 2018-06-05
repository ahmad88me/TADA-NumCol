from functools import partial
import modeling
from modeling import update_model_progress_for_partial, update_model_state
from modeling import ModelClass
import easysparql
import features
import traceback
from util import get_numericals, remove_outliers
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def compute_features_from_endpoint(model, class_property_uris, min_num_of_objects, update_func):
    """
    :param endpoint:
    :param class_property_uris:
    :param min_num_of_objects:
    :param update_func:
    :return: list of (cluster,feature) pairs
    """
    update_model_state(model=model, new_progress=0, new_notes="extracting values from gathered class/property")
    percentage_of_numerical = 0.5
    idx = 0
    total_num_of_queries = 0

    # calculate the required num of queries
    for class_uri in class_property_uris.keys():
        total_num_of_queries += len(class_property_uris[class_uri])

    for class_uri in class_property_uris.keys():
        logger.info("\nproperties for %s are %d" % (class_uri, len(class_property_uris[class_uri])))
        for property_uri in class_property_uris[class_uri]:
            # logger.debug("getting objects for: %s"%property_uri)
            raw_col = easysparql.get_objects(endpoint=model.knowledge_graph, class_uri=class_uri,
                                             property_uri=property_uri)

            if len(raw_col) > min_num_of_objects:
                col = get_numericals(column=raw_col)
                if len(col) > percentage_of_numerical * len(raw_col):
                    col = remove_outliers(col)
                    if len(col) > min_num_of_objects:
                        logger.debug("success: %s" % (property_uri))
                        # features_vector = features.compute_features(col, [features.mean, features.std, features.q1,
                        #                                                   features.q3])
                        features_vector = features.compute_curr_features(col)
                        cluster_name = "%s %s" % (class_uri, property_uri)
                        logger.debug("cluster: %s" % cluster_name)
                        modeling.add_cluster_to_model(model=model, name=cluster_name, features=features_vector)
                    else:
                        logger.debug("\n***%s only has %d values" % (property_uri, len(col)))
                else:
                    logger.debug("%s only has %d/%d numerical values" % (property_uri, len(raw_col), len(col)))
            update_func(int(idx * 1.0 / total_num_of_queries * 100))


def get_models_properties(model, update_progress_func):
    classes_properties_uris = {}
    classes_uris = model.modelclass_set.all()
    logger.debug("will loop classes uris")
    for idx, class_uri in enumerate(classes_uris):
        print(idx)
        update_progress_func(int(idx * 1.0 / len(classes_uris) * 100))
        from config import min_num_of_entities_per_property
        properties = easysparql.get_properties_for_class_abox(endpoint=model.knowledge_graph,
                                                              class_uri=class_uri.class_uri,
                                                              raiseexception=True,
                                                              min_num=min_num_of_entities_per_property)
        classes_properties_uris[class_uri.class_uri] = properties
        # for prop in properties:
        #     classes_properties_uris.append((class_uri, prop))
    update_progress_func(100)
    return classes_properties_uris


def train_abox(model):
    try:
        logger.info("train abox")
        update_progress_func = partial(update_model_progress_for_partial, model)
        update_model_state(model=model, new_state='Running', new_progress=0,
                           new_notes="Extracting numerical class/property combinations")
        logger.debug("will ask for properties")
        classes_properties_dict = get_models_properties(model=model, update_progress_func=update_progress_func)
        from config import min_num_of_objects
        compute_features_from_endpoint(model=model, class_property_uris=classes_properties_dict,
                                       min_num_of_objects=min_num_of_objects, update_func=update_progress_func)

        logger.info("train abox is completed successfully")
        update_model_state(model=model, new_progress=100, new_state="Completed", new_notes="Completed")
    except Exception as e:
        update_model_state(model=model, new_state="Stopped", new_notes="Raised error: " + str(e))
        traceback.print_exc()
