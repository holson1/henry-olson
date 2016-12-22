# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-15 01:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bart', '0007_parameter_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='StationAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='station',
            name='aliases',
            field=models.ManyToManyField(to='bart.StationAlias'),
        ),
    ]
