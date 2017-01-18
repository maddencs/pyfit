# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-18 02:16
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import workout.models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0003_auto_20170118_0150'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise_type', models.CharField(choices=[('RESISTANCE', 'Resistance'), ('CARDIO', 'Cardio'), ('SPORT', 'Sport')], default='RESISTANCE', max_length=30)),
                ('exercise_name', models.CharField(choices=[('BENCH_PRESS', 'Bench Press'), ('OVERHEAD_PRESS', 'Overhead Press')], default='Custom Exercise', max_length=250)),
                ('sets', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=10), default=[], size=10)),
                ('rest_duration', models.IntegerField(default=60)),
                ('routine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='workout.Routine')),
            ],
            bases=(models.Model, workout.models.ModelMixin),
        ),
        migrations.RemoveField(
            model_name='workout',
            name='routine',
        ),
        migrations.DeleteModel(
            name='Workout',
        ),
    ]
