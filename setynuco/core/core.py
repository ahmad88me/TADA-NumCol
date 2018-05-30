from functools import partial
import modeling
from modeling import update_model_progress_for_partial, update_model_state
from modeling import ModelClass
import easysparql





def get_properties_objects(endpoint, class_property_uris, min_num_of_objects):
    idx = 0
    cols = []
    for class_uri in class_property_uris.keys():
        for property_uri in class_property_uris[class_uri]:
            idx += 1
            col = easysparql.get_objects_as_list(endpoint=endpoint, class_uri=class_uri, property_uri=property_uri,
                                                 isnumericfilter=False)
            if col.shape[0] != 0 and col.shape[0] >= min_num_of_objects:
                cols.append(col)
                single_meta = {}
                single_meta["type"] = class_property_string_representation(class_uri, property_uri)
                single_meta["from_index"] = meta_start_idx
                meta_start_idx += col.shape[0]
                single_meta["to_index"] = meta_start_idx
                meta_data.append(single_meta)
                update_func(int(idx * 1.0 / num_of_uris * 100))




def get_models_properties(model, update_progress_func):
    classes_properties_uris = {}
    classes_uris = model.modelclass_set.all()
    for idx, class_uri in enumerate(classes_uris):
        update_progress_func(int(idx * 1.0 / len(classes_uris) * 100))
        properties = easysparql.get_properties_for_class_abox(endpoint=model.knowledge_graph, class_uri=class_uri,
                                                              raiseexception=True)
        classes_properties_uris[class_uri] = properties
        for prop in properties:
            classes_properties_uris.append((class_uri, prop))
    update_progress_func(100)
    update_model_state(model=model, new_progress=0, new_notes="extracting values from gathered class/property")
    return classes_properties_uris


def explore_and_train_abox(model, min_num_of_objects):
    try:
        update_progress_func = partial(update_model_progress_for_partial, model)
        update_model_state(model=model, new_state='Running', new_progress=0,
                           new_notes="Extracting numerical class/property combinations")
        classes_properties_dict = get_models_properties(model=model, update_progress_func=update_progress_func)



        data, meta_data = data_extraction.data_and_meta_from_class_property_uris(
            endpoint=endpoint, class_property_uris=classes_properties_uris, update_func=update_progress_func,
            isnumericfilter=False, min_num_of_objects=min_num_of_objects)

        update_model_state(model=model, new_progress=0, new_notes="training the model")
        if data is None:
            update_model_state(model=model, new_progress=0, new_state='Stopped',
                               new_notes="No data is extracted from the endpoint")
            return
        if np.any(np.isnan(data)):
            print "explore_and_train_abox> there is a nan in the data"
            print "**************************"
        else:
            print "explore_and_train_abox> no nans in the data"
        model = learning.train_with_data_and_meta(data=data, meta_data=meta_data, update_func=update_progress_func)
        if model is None:
            update_model_state(model_id=model_id, new_state=MLModel.STOPPED,
                               new_notes="leaning failed as model is None")
            return
        update_model_state(model_id=model_id, new_progress=0, new_notes="organizing the clusters")
        meta_with_clusters = learning.get_cluster_for_meta(training_meta=meta_data, testing_meta=meta_data,
                                                           update_func=update_progress_func)
        update_model_state(model_id=model_id, new_progress=0, new_notes="Saving the model data")
        model_file_name = data_extraction.save_model(model=model, meta_data=meta_data, file_name=str(model_id) + " - ")
        if model_file_name is not None:
            m = MLModel.objects.filter(id=model_id)
            if len(m) == 1:
                m = m[0]
                m.file_name = model_file_name
                m.save()
                update_model_state(model=model, new_progress=100, new_state="Completed", new_notes="Completed")
            else:
                update_model_state(model=model, new_progress=0, new_state="Stopped", new_notes="model is deleted")
        else:
            update_model_state(model=model, new_progress=0, new_state="Stopped", new_notes="Error Saving the model")
    except Exception as e:
        print "explore_and_train_abox> Exception %s" % str(e)
        traceback.print_exc()
        update_model_state(model=model, new_state="Stopped", new_notes="Raised error: " + str(e))















def data_and_meta_from_class_property_uris(endpoint=None, class_property_uris=[], update_func=None,
                                           isnumericfilter=True, min_num_of_objects=0):
    """
    get data and meta data from given classes and properties
    a single meta data contains the following: type, from_index and to_index
    :param class_property_uris: a list or triples, each triple is composed of two values, class and property
    :param isnumericfilter:
    :return: data, meta data
    """
    print "\n*********************************************"
    print "*   data_and_meta_from_class_property_uris  *"
    print "*********************************************\n"
    if endpoint is None:
        print "data_and_meta_from_class_property_uris> endpoint should not be None"
        return None, None
    cols = []
    meta_data = []
    meta_start_idx = 0
    num_of_uris = len(class_property_uris)

    if update_func is None:
        for idx, c_p_uri in enumerate(class_property_uris):
            class_uri, propert_uri = c_p_uri
            print "--------------- extraction ------------------------"
            print "combination: %d" % idx
            print "class: %s" % class_uri
            print "property: %s" % propert_uri
            col = easysparql.get_objects_as_list(endpoint=endpoint, class_uri=class_uri, property_uri=propert_uri,
                                                 isnumericfilter=isnumericfilter)
            if col.shape[0] != 0 and col.shape[0] >= min_num_of_objects:
                cols.append(col)
                single_meta = {}
                single_meta["type"] = class_property_string_representation(class_uri, propert_uri)
                single_meta["from_index"] = meta_start_idx
                meta_start_idx += col.shape[0]
                single_meta["to_index"] = meta_start_idx
                meta_data.append(single_meta)
    else:
        for idx, c_p_uri in enumerate(class_property_uris):
            class_uri, propert_uri = c_p_uri
            print "--------------- extraction ------------------------"
            print "combination: %d" % idx
            print "class: %s" % class_uri
            print "property: %s" % propert_uri
            col = easysparql.get_objects_as_list(endpoint=endpoint, class_uri=class_uri, property_uri=propert_uri,
                                                 isnumericfilter=isnumericfilter)
            if col.shape[0] != 0 and col.shape[0] >= min_num_of_objects:
                cols.append(col)
                single_meta = {}
                single_meta["type"] = class_property_string_representation(class_uri, propert_uri)
                single_meta["from_index"] = meta_start_idx
                meta_start_idx += col.shape[0]
                single_meta["to_index"] = meta_start_idx
                meta_data.append(single_meta)
                update_func(int(idx*1.0/num_of_uris * 100))

    if update_func is not None:
        update_func(100)

    if len(cols) > 0:
        data = np.array([])
        data.shape = (0, cols[0].shape[1])
        for col in cols:
            data = np.append(data, col, axis=0)
        data = get_features(data)
        return data, meta_data
    else:
        return None, None



