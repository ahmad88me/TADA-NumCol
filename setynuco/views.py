from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.files import File
from datetime import datetime
from subprocess import Popen
import os
from models import MLModel, PredictionRun
import numpy as np
import random
import string
import settings


class ModelAdd(TemplateView):
    template_name = 'model_add.html'

    def post(self, request):
        error_msg = ''
        if 'url' not in request.POST:
            error_msg = 'url is not passed'
        if 'name' not in request.POST:
            error_msg = 'name is not passed'
        if len(request.POST.getlist('class_uri')) == 0 and request.POST['class_uris'].strip() == "":
            error_msg = 'There should be at least one class uri'
        if error_msg != '':
            return render(request, self.template_name, {'error_msg': error_msg})
        name = request.POST['name']
        knowledgegraph = request.POST['url']
        classes_str = " ".join(request.POST.getlist('class_uri'))
        from core.djangomodels import venv_python, proj_path
        comm = "%s %s model_add --name \"%s\" --knowledge_graph \"%s\" --class_uris %s" % (venv_python,os.path.join(proj_path, 'core', 'cmd.py'), name, knowledgegraph, classes_str)
        print(comm)
        Popen(comm, shell=True)
        return redirect('/model_list')


def model_list(request):
    return render(request, 'model_list.html', {'models': MLModel.objects.all()})


class PredictionAdd(TemplateView):
    template_name = 'prediction_add.html'

    def get(self, request):
        return render(request, self.template_name, {'models': MLModel.objects.all()})

    def post(self, request):
        name = request.POST['name']
        model_id = request.POST['model_id']
        models = MLModel.objects.filter(id=model_id)
        if len(models) != 1:
            return render(request, self.template_name, {'models': MLModel.objects.all(),
                                                    'error_msg': 'this model is not longer exists'})
        model = models[0]
        input_file = request.FILES['csvfile']
        dest_file_name = name + ' - ' + random_string(length=4) + '.csv'
        dest_file_dir = os.path.join(settings.UPLOAD_DIR, dest_file_name)
        if handle_uploaded_file(uploaded_file=input_file,
                                destination_file=dest_file_dir):
            pr = PredictionRun(name=name, model=model, created_on=datetime.now(), input_file=dest_file_dir)
            pr.save()
            from core.djangomodels import venv_python, proj_path
            comm = "%s %s predict --id %d" % (venv_python, os.path.join(proj_path, 'core', 'cmd.py'), pr.id)
            print(comm)
            Popen(comm, shell=True)
            return redirect('/prediction_list')
        else:
            return render(request, self.template_name, {'models': MLModel.objects.filter(state=MLModel.COMPLETE),
                                                    'error_msg': 'we could not handle any of the files,' +
                                                                 ' make sure they are text csv files'})


def prediction_list(request):
    if 'annotation_only' in request.GET:
        predictions = [p for p in PredictionRun.objects.all() if len(p.columnprediction_set.all()) > 0]
        return render(request, 'prediction_list.html', {'predictions': predictions})
    return render(request, 'prediction_list.html', {'predictions': PredictionRun.objects.all()})


def clusters_for_prediction(request):
    prediction_id = request.GET['id']
    prediction_run = PredictionRun.objects.get(id=prediction_id)
    return render(request, 'clusters_for_prediction.html',
                   {'column_predictions': prediction_run.columnprediction_set.all(), 'prediction_run': prediction_run})


def handle_uploaded_file(uploaded_file=None, destination_file=None):
    if uploaded_file is None:
        print "handle_uploaded_file> uploaded_file should not be None"
        return False
    if destination_file is None:
        print "handle_uploaded_file> destination_file should not be None"
        return False
    f = uploaded_file
    with open(destination_file, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return True


def random_string(length=4):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def home(request):
    return render(request, 'home.html')