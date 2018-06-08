import numpy as np
from fuzzycmeans import FCM
from modeling import PredictionRun, ColumnPrediction, CCMembership
import features
import util
import logging
import chardet
from datetime import datetime

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def get_numerical_columns(data):
    """
    :param data: an np matrix
    :return: an np matrix of numerical columns
    """
    percentage_of_num_per_col = 0.5
    num_cols = []
    new_i = 0
    new_old_idx_matching = {}
    for i in range(len(data[0])):
        raw_col = data[:, i]
        col = util.get_numericals(raw_col)
        if len(col) > percentage_of_num_per_col * len(raw_col):
            num_cols.append(col)
            new_old_idx_matching[new_i] = i
            new_i += 1
    return np.array(num_cols).T, new_old_idx_matching


def load_mlmodel_into_fcm(model):
    """
    :param model: MLModel
    :param data: matrix input as np array
    :return: FCM model
    """
    num_of_cols = len(model.cluster_set.all())
    centers = []
    for clus_model in model.cluster_set.all():
        logger.debug("load_mlmodel_into_fcm> getting clus %s" % clus_model.name)
        p = clus_model.center.split(',')
        centers.append(p)
    centers_np = np.array(centers, dtype='f')
    # logger.debug("Centers: ")
    # logger.debug(centers_np)
    fcm = FCM(n_clusters=num_of_cols)
    fcm.cluster_centers_ = centers_np
    data = centers_np
    logger.debug("load_mlmodel_into_fcm> will fit the data with %d clusters" % num_of_cols)
    fcm.fit(data, range(num_of_cols))
    logger.info("generated the FCM model from the MLModel")
    return fcm


def predict(prediction_run_id):
    prediction_run = PredictionRun.objects.get(id=prediction_run_id)
    file_dir = prediction_run.input_file.path
    # f = open(file_dir)
    # chardet.detect(f.read())
    # raw_data = np.loadtxt(file_dir, delimiter=',', skiprows=1)
    raw_data = np.genfromtxt(file_dir, delimiter=',', skip_header=1, invalid_raise=False)  # invalid_raise to skip rows with excessive number of files
    logger.debug("asking for numerical columns")
    data, new_old_idx_matching = get_numerical_columns(raw_data)
    num_of_cols = len(data[0])
    if num_of_cols > 0:
        logger.debug("will load the MLModel")
        fcm = load_mlmodel_into_fcm(prediction_run.model)

        for i in range(num_of_cols):
            col = data[:, i]
            logger.debug("num col:")
            logger.debug(col)
            col_fea = features.compute_curr_features(col)
            col_fea = np.array(col_fea)
            col_fea.shape = (col_fea.shape[0], 1)
            col_fea = col_fea.T
            logger.debug("col fea val:")
            logger.debug(col_fea)
            logger.debug("col fea shape: ")
            logger.debug(col_fea.shape)
            membership_vector = fcm.predict(col_fea)[0]
            logger.debug("membership vector: ")
            logger.debug(membership_vector)
            max_num_of_prediction_memberships = 10
            small_value = np.amin(membership_vector) - 1  # could be subtracted from any value
            col_fea_str = ",".join([str(util.round_acc(v)) for v in col_fea[0]])
            column_prediction = ColumnPrediction(column_no=new_old_idx_matching[i], prediction_run=prediction_run, features=col_fea_str)
            column_prediction.save()
            for k in range(max_num_of_prediction_memberships):
                # here I have to save the cluster ... to be continue
                # fcm_clus_idx = -1
                max_idx = np.argmax(membership_vector)
                # for clus_model in prediction_run.model.cluster_set.all():
                #     if fcm_clus_idx >= 0:
                #         break
                #     for idx, fcm_center in enumerate(fcm.cluster_centers_):
                #         if np.array_equal(np.array(clus_model.center.split(',')), fcm_center):
                #             fcm_clus_idx = idx
                #             break
                # if fcm_clus_idx <= 0:
                #     print("fcm centers: ")
                #     print(fcm.cluster_centers_)
                #     print("clusters: ")
                #     print([c.center for c in prediction_run.model.cluster_set.all()])
                #     raise Exception("could not find a matching center")
                clus_center = fcm.cluster_centers_[max_idx]
                center_str = ",".join(str(util.round_acc(c)) for c in clus_center)
                matching_clusters = prediction_run.model.cluster_set.filter(center=center_str)
                if len(matching_clusters) == 0:
                    # logger.error("fcm centers: ")
                    # logger.error(fcm.cluster_centers_)
                    logger.warning("clusters: ")
                    logger.warning([c.center for c in prediction_run.model.cluster_set.all()])
                    logger.warning("was looking for the center: ")
                    logger.warning(center_str)
                    #raise Exception("could not find a matching center")
                    logger.warning("could not find a matching center, hence will find the closet cluster")

                    min_diff = 100
                    matching_clus_model = None
                    for clus_model in prediction_run.model.cluster_set.all():
                        local_diff = np.linalg.norm(np.array(clus_model.center.split(','), dtype='f') - clus_center)
                        if local_diff < min_diff:
                            matching_clus_model = clus_model
                    if matching_clus_model is None:
                        logger.error("could not find a close match to the cluster")
                        raise Exception("could not find a close match to the cluster")
                    logger.debug("matching clus: ")
                    logger.debug(matching_clus_model.center)
                    matching_clusters = [matching_clus_model]

                membership_model = CCMembership(column_prediction=column_prediction, membership=membership_vector[max_idx], cluster=matching_clusters[0])
                membership_model.save()
                membership_vector[max_idx] = small_value
        prediction_run.finished_on = datetime.now()
        prediction_run.save()

    else:
        logger.warning("There are zero numerical columns, hence Done.")




