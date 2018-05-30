from django.db import models
from datetime import datetime


class MLModel(models.Model):
    name = models.CharField(max_length=120)
    knowledge_graph = models.URLField()
    created_on = models.DateTimeField(default=datetime.now())
    progress = models.PositiveIntegerField(default=0)
    notes = models.TextField()


class Cluster(models.Model):
    name = models.CharField(max_length=120)
    center = models.TextField()  # comma separated


class ModelClass(models.Model):
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    class_uri = models.URLField()


class PredictionRun(models.Model):
    name = models.CharField(max_length=120)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=datetime.now())
    finished_on = models.DateTimeField(default=datetime.now())
    input_file = models.FileField()


class ColumnPrediction(models.Model):
    prediction_run = models.ForeignKey(PredictionRun, on_delete=models.CASCADE)
    column_no = models.PositiveIntegerField()
    membership_vector = models.TextField()  # comma separated
