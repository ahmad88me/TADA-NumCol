from django.contrib import admin
from setynuco.models import MLModel, Cluster, ModelClass, PredictionRun, ColumnPrediction, CCMembership

admin.site.register(MLModel)
admin.site.register(Cluster)
admin.site.register(ModelClass)
admin.site.register(PredictionRun)
admin.site.register(ColumnPrediction)
admin.site.register(CCMembership)