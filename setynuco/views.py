from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from subprocess import Popen
import os
from models import MLModel


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


def home(request):
    return render(request, 'home.html')