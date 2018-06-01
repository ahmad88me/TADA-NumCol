from django.contrib import admin
from setynuco.models import MLModel, Cluster, ModelClass

admin.site.register(MLModel)
admin.site.register(Cluster)
admin.site.register(ModelClass)