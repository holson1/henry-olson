from __future__ import unicode_literals

from django.db import models
import json
import uuid

param_types = [('station', 'station'), ('dir', 'dir'), ('num_trains', 'num_trains'), ('command', 'command')]

# Create your models here.
class Command(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    api_cmd = models.CharField(max_length=50)
    link = models.CharField(max_length=100, blank=True)
    parser = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Parameter(models.Model):
    name = models.CharField(max_length=30, blank=True)
    param_type = models.CharField(max_length=40, choices=param_types)
    default_value = models.CharField(max_length=100, blank=True)
    required = models.BooleanField(default=False)
    commands = models.ManyToManyField(Command)
    order = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.name

class Station(models.Model):
    key = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s" % (self.name)

class StationAlias(models.Model):
    alias = models.CharField(max_length=200)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)