# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-26 22:36
from __future__ import unicode_literals
from django.db import migrations


def create_groups(apps, schema_editor):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    Observatory = apps.get_model('broker', 'Observatory')
    Alert = apps.get_model('broker', 'Alert')
    Assignment = apps.get_model('broker', 'Assignment')

    brokeradmins_group, created = Group.objects.get_or_create(name='broker_admins')
    if created:
        actions = ['add', 'change', 'delete']
        ct = ContentType.objects.get_for_model(Observatory)
        obs_perms = [Permission.objects.create(
            codename='can_{}_observatory'.format(act),
            name='Can {} observatory'.format(act),
            content_type=ct) for act in actions]

        ct = ContentType.objects.get_for_model(Assignment)
        assgn_perms = [Permission.objects.create(
            codename='can_{}_assignment'.format(act),
            name='Can {} assignment'.format(act),
            content_type=ct) for act in actions]

        ct = ContentType.objects.get_for_model(Alert)
        alert_perms = [Permission.objects.create(
            codename='can_{}_alert'.format(act),
            name='Can {} alert'.format(act),
            content_type=ct) for act in actions]
        brokeradmins_group.permissions.add(*(obs_perms + assgn_perms + alert_perms))

    telescopeop_group, created = Group.objects.get_or_create(name='telescope_operators')



class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0001_initial'),
    ]

    operations = [
            migrations.RunPython(create_groups),
    ]
