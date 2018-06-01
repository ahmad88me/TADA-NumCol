


#################################################################
#                  Command line interface                       #
#################################################################
import argparse
import training
import modeling

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('task', type=str)
    parser.add_argument('--name')
    parser.add_argument('--knowledge_graph')
    parser.add_argument('--class_uris', action='append', nargs='*')
    # parser.add_argument('runid', type=int, metavar='Annotation_Run_ID', help='the id of the Annotation Run ')
    # parser.add_argument('--csvfiles', action='append', nargs='+', help='the list of csv files to be annotated')
    # parser.add_argument('--dotype', action='store_true', help='To conclude the type/class of the given csv file')
    args = parser.parse_args()
    if args.task == 'model_add':
        model = modeling.model_add(name=args.name, knowledge_graph=args.knowledge_graph, class_uris=args.class_uris[0])
        training.train_abox(model=model, min_num_of_objects=30)
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
