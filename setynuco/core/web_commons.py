from djangomodels import *
from setynuco import settings
import chardet
import json
import os
import csv

BASE_DIR = settings.BASE_DIR


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


web_commons_transformation()
