from django.shortcuts import render, redirect
from django.views.generic import TemplateView


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


            #
            #
            # mlmodel = MLModel()
            # mlmodel.name = clean_string(request.POST['name'])
            # if mlmodel.name.strip() == '':
            #     mlmodel.name = random_string(length=6)
            # mlmodel.url = request.POST['url']
            #
            #
            # mlmodel.save()
            # if request.POST['class_uris'].strip() == "":
            #     class_uris = request.POST.getlist('class_uri')
            # else:
            #     class_uris = []
            #     for cu in request.POST['class_uris'].split(','):
            #         class_uris.append(cu.strip())
            # core.explore_and_train_abox(endpoint=mlmodel.url, model_id=mlmodel.id, min_num_of_objects=30,
            #                             classes_uris=class_uris)



    return redirect('list_models')




def home(request):
    return render(request, 'home.html')