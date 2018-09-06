import numpy as np
import pandas as pd
from fuzzycmeans import FCM

import features
import util

import os
import logging
from logger import set_config
from setynuco.settings import UPLOAD_DIR


logger = set_config(logging.getLogger(__name__))


def load_model_from_file(concepts):
    """
    :param concepts: list of classes URIs
    :return: FCM model
    """
    model_file_dir = os.path.join(UPLOAD_DIR, "models.csv")
    df = pd.read_csv(model_file_dir, header=0)
    clusters = []
    just_centers = []
    for index, row in df.iterrows():
        class_uri = row[0]
        property_uri = row[1]
        if class_uri in concepts:
            mean, median, std = row[2:]
            d = {'class_uri': class_uri,
                 'property_uri': property_uri,
                 #'center': np.array([mean, median, std], dtype='f')
            }
            clusters.append(d)
            #just_centers.append(d['center'])
            just_centers.append(np.array([mean, median, std], dtype='f'))

    fcm = FCM(n_clusters=len(clusters), max_iter=1, logger=logger)
    centers_np = np.array(just_centers, dtype='f')
    fcm.cluster_centers_ = centers_np
    data = centers_np
    logger.debug("load_mlmodel_into_fcm> will fit the data with %d clusters" % len(clusters))
    fcm.fit(data, range(len(clusters)))
    # logger.debug("load_model_from_file> will fit the data with %d clusters" % len(just_centers))
    # fcm.fit(fcm.cluster_centers_, range(len(just_centers)))
    logger.info("load_model_from_file> generated the FCM model from the MLModel")
    return fcm, clusters


def predict(csv_dir, concepts):
    """
    annotate the numerical columns in the given CSV file
    :param csv_dir:
    :return:
    """
    predictions = []  # a list of predictions, each prediction is a dict
    logger.debug("predict> reading the CSV file")
    raw_data = pd.read_csv(csv_dir).values
    logger.debug("predict> asking for numerical columns")
    data_list_of_cols, new_old_idx_matching = util.get_numerical_columns(raw_data)
    if len(data_list_of_cols) == 0:
        logger.debug("predict> no numerical data is found")
        return
    num_of_cols = len(data_list_of_cols)
    if num_of_cols > 0:
        logger.debug("predict> will load the MLModel")
        fcm, clusters = load_model_from_file(concepts=concepts)
        logger.debug("predict> number of numerical columns %d" % num_of_cols)
        max_num_of_prediction_memberships = min(10, len(clusters))
        out_file_name = csv_dir[:-4]+"-predictions.csv"
        print("out file name: "+out_file_name)
        out_file = open(out_file_name, "w")
        for i in range(num_of_cols):
            col = data_list_of_cols[i]
            col_fea = features.compute_curr_features(col)
            col_fea = np.array(col_fea)
            col_fea.shape = (col_fea.shape[0], 1)
            col_fea = col_fea.T
            logger.debug("col fea val:")
            logger.debug(col_fea)
            logger.debug("col fea shape: ")
            logger.debug(col_fea.shape)
            membership_vector = fcm.predict(col_fea)[0]
            small_value = np.amin(membership_vector) - 1  # could be subtracted from any value
            col_fea_str = ",".join([str(util.round_acc(v)) for v in col_fea[0]])
            print("Col: %d"%new_old_idx_matching[i])
            for k in range(max_num_of_prediction_memberships):
                max_idx = np.argmax(membership_vector)
                #clus_center = fcm.cluster_centers_[max_idx]
                print("\t %20s %20s %.6f" % (clusters[max_idx]["class_uri"], clusters[max_idx]["property_uri"], membership_vector[max_idx]))
                out_file.write('''"%s","%s",%d, %.6f\n''' % (csv_dir, clusters[max_idx]["property_uri"], k+1, membership_vector[max_idx]))
                membership_vector[max_idx] = small_value
        out_file.close()
    else:
        logger.warning("predict> There are zero numerical columns, hence Done.")



