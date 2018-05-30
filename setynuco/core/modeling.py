#################################################################
#           TO make this app compatible with Django             #
#################################################################
import os
import sys

proj_path = (os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
venv_python = os.path.join(proj_path, '.venv', 'bin', 'python')
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setynuco.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

#################################################################
#                        Modeling                               #
#################################################################

from setynuco.models import *


def model_add(name, knowledge_graph, class_uris):
    mlmodel = MLModel()
    mlmodel.name = name
    mlmodel.knowledge_graph = knowledge_graph
    mlmodel.save()
    for curi in class_uris:
        ModelClass(model=mlmodel, class_uri=curi).save()
    return mlmodel


def update_model_progress_for_partial(model, new_progress):
    return update_model_state(model=model, new_progress=new_progress)


def update_model_state(model, new_state=None, new_notes=None, new_progress=None):
    if new_state is not None:
        model.state = new_state
    if new_notes is not None:
        model.notes = new_notes
    if new_progress is not None:
        model.progress = new_progress
    model.save()
    return model



