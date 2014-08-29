# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timer', '0001_initial'),
        ('legalaid', '0001_initial'),
        ('cla_eventlog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='case',
            field=models.ForeignKey(to='legalaid.Case'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='log',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='log',
            name='timer',
            field=models.ForeignKey(blank=True, to='timer.Timer', null=True),
            preserve_default=True,
        ),
    ]
