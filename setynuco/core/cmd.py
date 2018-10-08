


#################################################################
#                  Command line interface                       #
#################################################################
import argparse
import training
import modeling
import prediction
import training_from_file
import prediction_from_file
import training_from_hdt

# import subprocess
# import sys
# print sys.argv
# import os
# print "working dir: "+os.getcwd()
# print "filedir: "+os.path.dirname(__file__)
# print "combined: "+os.path.dirname(os.getcwd())
#
# proc = subprocess.Popen(['pwd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# wd, err = proc.communicate()
# if err:
#     print >> sys.stderr, err
# else:
#     print wd,

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('task', type=str)
    parser.add_argument('--name')
    parser.add_argument('--id')
    parser.add_argument('--knowledge_graph')
    parser.add_argument('--class_uris', action='append', nargs='*')
    parser.add_argument('--trainingfile', action='store', help='The training file that includes all classes, properties, and their values')
    parser.add_argument('--csv', action='store', help='The testing CSV file to be annotated')
    parser.add_argument('--hdt', action='store', help='The HDT file that contains the knowledge graph(s)')
    # parser.add_argument('runid', type=int, metavar='Annotation_Run_ID', help='the id of the Annotation Run ')
    # parser.add_argument('--csvfiles', action='append', nargs='+', help='the list of csv files to be annotated')
    # parser.add_argument('--dotype', action='store_true', help='To conclude the type/class of the given csv file')
    args = parser.parse_args()
    if args.task == 'model_add':
        model = modeling.model_add(name=args.name, knowledge_graph=args.knowledge_graph, class_uris=args.class_uris[0])
        training.train_abox(model=model)
    elif args.task == "predict":
        prediction.predict(args.id)
    # if args.csvfiles and len(args.csvfiles) > 0:
    #     print 'csvfiles: %s' % args.csvfiles
    #     print "adding dataset"
    #     annotate_csvs(ann_run_id=args.runid, hierarchy=False, files=args.csvfiles[0], gen_class_eli=False,
    #                   endpoint="http://dbpedia.org/sparql")
    #     print "data set is added successfully. Done"
    # if args.dotype:
    #     ann_run = OnlineAnnotationRun.objects.get(id=args.runid)
    #     print 'typing the csv file'
    #     dotype(ann_run=ann_run, endpoint=endpoint)
    #     print 'done typing the csv file'
    elif args.task == "modelfromfile":
        if args.trainingfile is None:
            print("Error, expecting the option --trainingfile")
        elif args.trainingfile[0] != '/':
            # The reason that relative path does not work is because Django change the PWD directory.
            #abs_training_file_dir = os.path.join(os.getcwd(), args.trainingfile)
            #training_from_file.create_model(file_dir=abs_training_file_dir)
            print("Error, expecting absolute path")
        else:
            training_from_file.create_model(file_dir=args.trainingfile)
    elif args.task == "predictfromfile":
        if args.csv is None:
            print("Error, expecting a CSV file")
        elif args.csv[0] != '/':
            print("Error, expecting absolute path")
        else:
            prediction_from_file.predict(csv_dir=args.csv, concepts=args.class_uris[0])
    elif args.task == "modelfromhdt":
        if args.hdt is None:
            print("Error, expecting hdt file")
        else:
            training_from_hdt.workflow(args.hdt)

