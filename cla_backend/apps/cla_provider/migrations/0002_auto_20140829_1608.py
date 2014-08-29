# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cla_provider', '0001_initial'),
        ('legalaid', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='providerallocation',
            name='category',
            field=models.ForeignKey(to='legalaid.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='providerallocation',
            name='provider',
            field=models.ForeignKey(to='cla_provider.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='law_category',
            field=models.ManyToManyField(to='legalaid.Category', through='cla_provider.ProviderAllocation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='outofhoursrota',
            name='category',
            field=models.ForeignKey(to='legalaid.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='outofhoursrota',
            name='provider',
            field=models.ForeignKey(to='cla_provider.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feedback',
            name='created_by',
            field=models.ForeignKey(to='cla_provider.Staff'),
            preserve_default=True,
        ),
    ]
