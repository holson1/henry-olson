from __future__ import unicode_literals

from django.db import models
import json
import uuid

param_types = [('station', 'station'), ('dir', 'dir')]

# Create your models here.
class Command(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    api_cmd = models.CharField(max_length=50)
    link = models.CharField(max_length=100)
    parser = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Parameter(models.Model):
    name = models.CharField(max_length=30)
    param_type = models.CharField(max_length=40, choices=param_types)
    commands = models.ManyToManyField(Command)

    def __unicode__(self):
        return self.name