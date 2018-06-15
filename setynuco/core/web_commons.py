from djangomodels import *
from setynuco import settings
import chardet
import json
import os
import csv
from subprocess import call
from datetime import datetime
import logging
from django.core.files import File

BASE_DIR = settings.BASE_DIR

logger = logging.getLogger(__name__)
handler = logging.FileHandler('web_commons.log')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def web_commons_json_table_to_csv(in_file_dir, out_file_dir):
    fin = open(in_file_dir)
    s_raw = fin.read()
    detected_encoding = chardet.detect(s_raw)
    s = s_raw.decode(detected_encoding['encoding'])
    j = json.loads(s)
    num_of_cols = len(j["relation"])
    cols = []
    for col_idx in range(num_of_cols):
        column_clean = []
        column_raw = j["relation"][col_idx]
        for e in column_raw:
            ee = e.replace('"', '').strip()
            ee = '"' + ee + '"'
            column_clean.append(ee)
        cols.append(column_clean)
    cols_in_order = map(list, zip(*cols))
    cols_in_str = []
    for col in cols_in_order:
        col_str = ",".join(col)
        cols_in_str.append(col_str)
    fout = open(out_file_dir, 'w')
    fout.write(("\n".join(cols_in_str)).encode('utf8'))
    fout.close()


def web_commons_transformation():
    input_base_url = "/Users/aalobaid/workspaces/Pyworkspace/tada/tadacode/local_data/web_commons_tables"
    output_base_url = os.path.join(BASE_DIR, "web_commons", "data")
    f = open(os.path.join(BASE_DIR, "web_commons", "web_commons_classes.csv"))
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
        file_name_with_ext, high_level_concept, concept_uri = row
        file_name_with_json = file_name_with_ext[:-7] + ".json"
        web_commons_json_table_to_csv(os.path.join(input_base_url, file_name_with_json),
                                      os.path.join(output_base_url, file_name_with_ext + ".csv"))
        print file_name_with_json, concept_uri


def create_model(name, class_uri):
    from setynuco.models import MLModel
    models = MLModel.objects.filter(name=name)
    if len(models) == 0:
        knowledgegraph = "https://dbpedia.org/sparql"
        classes_str = class_uri
        from setynuco.core.djangomodels import venv_python, proj_path
        comm = "%s %s model_add --name \"%s\" --knowledge_graph \"%s\" --class_uris %s" % (
            venv_python, os.path.join(proj_path, 'core', 'cmd.py'), name, knowledgegraph, classes_str)
        logger.debug(comm)
        call(comm, shell=True)
    else:
        logger.debug("%s already exists" % name)


def predict(prediction_name, model_name):
    from setynuco.models import MLModel, PredictionRun
    models = MLModel.objects.filter(name=model_name)
    if len(models) != 1:
        return
    model = models[0]
    # pr = PredictionRun(name=prediction_name, model=model, created_on=datetime.now(), input_file=input_file)
    # pr.save()
    prs = PredictionRun.objects.filter(name=prediction_name)
    if len(prs) == 0:
        logger.error("predict> pr %s not found" % prediction_name)
        return
    pr = prs[0]
    # if pr.status == PredictionRun.STATUS_NOTSTARTED:
    if pr.status == PredictionRun.STATUS_RUNNING:
        from setynuco.core.djangomodels import venv_python, proj_path
        comm = "%s %s predict --id %d" % (venv_python, os.path.join(proj_path, 'core', 'cmd.py'), pr.id)
        logger.debug(comm)
        call(comm, shell=True)
    else:
        logger.debug("pr %d %s is already done" % (pr.id, pr.name))


def create_empty_prediction(prediction_name, model_name, input_file):
    from setynuco.models import MLModel, PredictionRun
    models = MLModel.objects.filter(name=model_name)
    if len(models) != 1:
        logger.warning("model %s is not found" % model_name)
        return
    model = models[0]
    prs = PredictionRun.objects.filter(name=prediction_name)
    if len(prs) == 0:
        logger.debug("create_empty_prediction> creating %s" % prediction_name)
        pr = PredictionRun(name=prediction_name, model=model, created_on=datetime.now(), input_file=input_file)
        pr.save()
    else:
        logger.debug("create_empty_prediction> prediction exists %s" % prediction_name)


def run_experiment():
    data_dir = os.path.join(BASE_DIR, "web_commons", "data")
    f = open(os.path.join(BASE_DIR, "web_commons", "web_commons_classes.csv"))
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
        file_name_with_ext, high_level_concept, concept_uri = row
        file_name = file_name_with_ext + ".csv"
        create_model(name=high_level_concept, class_uri=concept_uri)
        ff = open(os.path.join(data_dir, file_name))
        create_empty_prediction(prediction_name=high_level_concept+" prediction "+file_name_with_ext,
                                model_name=high_level_concept, input_file=File(ff))
    f.close()
    f = open(os.path.join(BASE_DIR, "web_commons", "web_commons_classes.csv"))
    reader = csv.reader(f, delimiter=',', quotechar='"')
    logger.info("running the predictions")
    for row in reader:
        file_name_with_ext, high_level_concept, concept_uri = row
        predict(prediction_name=high_level_concept + " prediction " + file_name_with_ext, model_name=high_level_concept)


# web_commons_transformation()
run_experiment()