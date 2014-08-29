# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('code', models.CharField(max_length=20)),
                ('type', models.CharField(max_length=20, choices=[(b'outcome', b'outcome'), (b'system', b'system')])),
                ('level', models.PositiveSmallIntegerField(choices=[(29, b'HIGH'), (21, b'MODERATE'), (11, b'MINOR')])),
                ('notes', models.TextField(null=True, blank=True)),
                ('patch', jsonfield.fields.JSONField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
    ]
