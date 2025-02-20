# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-16 16:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctmoinaug', '0002_auto_20180412_2019'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='school',
        ),
        migrations.AddField(
            model_name='activity',
            name='comment',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='description',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='activity',
            name='organization',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='requires_chair',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activity',
            name='requires_power',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activity',
            name='requires_table',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activity',
            name='requires_volunteer',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='activity',
            name='activity',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='activity',
            name='status',
            field=models.CharField(choices=[('ok', 'Approved'), ('no', 'Rejected'), ('pe', 'Pending')], default='pe', max_length=2),
        ),
    ]
