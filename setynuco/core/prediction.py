import numpy as np
from fuzzycmeans import FCM
from modeling import PredictionRun, ColumnPrediction, CCMembership
import features
import util
import logging

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
        p = clus_model.center.split(',')
        centers.append(p)
    centers_np = np.array(centers)
    fcm = FCM(n_clusters=num_of_cols)
    fcm.cluster_centers_ = centers_np
    data = centers_np
    fcm.fit(data, range(num_of_cols))
    return fcm


def predict(prediction_run_id):
    prediction_run = PredictionRun.objects.get(prediction_run_id)
    file_dir = prediction_run.input_file.path
    raw_data = np.loadtxt(file_dir, delimiter=',', skiprows=1)
    data, new_old_idx_matching = get_numerical_columns(raw_data)
    num_of_cols = len(data[0])
    if num_of_cols > 0:
        fcm = load_mlmodel_into_fcm(prediction_run.model, data)
        for i in range(num_of_cols):
            col = data[:, i]
            col_fea = features.compute_curr_features(col)
            membership_vector = fcm.predict(col_fea)[0]
            max_num_of_prediction_memberships = 10
            small_value = np.amin(membership_vector)
            column_prediction = ColumnPrediction(column_no=new_old_idx_matching[i], prediction_run=prediction_run)
            column_prediction.save()
            for k in range(max_num_of_prediction_memberships):
                # here I have to save the cluster ... to be continue
                max_idx = np.argmax(membership_vector)
                membership_model = CCMembership(column_prediction=column_prediction, membership=membership_vector[max_idx], )

                membership_vector[max_idx] = small_value

                column_prediction = models.ForeignKey(ColumnPrediction, on_delete=models.CASCADE)
                cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
                membership = models.FloatField()




