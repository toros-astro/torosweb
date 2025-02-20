# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-13 18:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import stdimage.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('isCurrent', models.BooleanField(default=True)),
                ('start_datetime', models.DateTimeField(blank=True, null=True)),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('cadence_sec', models.FloatField(blank=True, null=True)),
                ('number_of_files', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('subset_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='winnow.Dataset')),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='date of experiment')),
                ('platform', models.CharField(choices=[('0', 'Weka'), ('1', 'RapidMiner'), ('2', 'scikit-learn'), ('3', 'Other')], default='0', max_length=1, verbose_name='software used')),
                ('other_platform_name', models.CharField(blank=True, max_length=20, null=True)),
                ('alg_name', models.CharField(max_length=50, verbose_name='algorithm name')),
                ('params_file', models.FileField(blank=True, max_length=50, null=True, upload_to='', verbose_name='parameter file name')),
                ('labels_file', models.FileField(blank=True, null=True, upload_to='', verbose_name='label file name')),
                ('featureset_infofile', models.FileField(blank=True, null=True, upload_to='', verbose_name='feature set file name')),
                ('featuretable_datafile', models.FileField(blank=True, null=True, upload_to='', verbose_name='feature table file name')),
                ('conf_mat_rr', models.IntegerField(verbose_name='reals classified as reals')),
                ('conf_mat_rb', models.IntegerField(verbose_name='reals classified as bogus')),
                ('conf_mat_br', models.IntegerField(verbose_name='bogus classified as reals')),
                ('conf_mat_bb', models.IntegerField(verbose_name='bogus classified as bogus')),
                ('confusion_table_file', models.FileField(blank=True, null=True, upload_to='', verbose_name='confusion matrix file name')),
                ('other_outputfiles', models.TextField(blank=True, null=True, verbose_name='other output files')),
                ('other_inputfiles', models.TextField(blank=True, null=True, verbose_name='other input files')),
                ('description', models.TextField(blank=True, null=True)),
                ('is_favorite', models.BooleanField(default=False)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='winnow.Dataset')),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('code', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField(choices=[(-1, 'Bogus'), (1, 'Real'), (0, 'Unclassified')], default=0)),
                ('isInteresting', models.BooleanField(default=False)),
                ('ranker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SEPInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thresh', models.FloatField()),
                ('npix', models.IntegerField()),
                ('tnpix', models.IntegerField()),
                ('xmin', models.IntegerField()),
                ('xmax', models.IntegerField()),
                ('ymin', models.IntegerField()),
                ('ymax', models.IntegerField()),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('x2', models.FloatField()),
                ('y2', models.FloatField()),
                ('xy', models.FloatField()),
                ('a', models.FloatField()),
                ('b', models.FloatField()),
                ('theta', models.FloatField()),
                ('cxx', models.FloatField()),
                ('cyy', models.FloatField()),
                ('cxy', models.FloatField()),
                ('cflux', models.FloatField()),
                ('flux', models.FloatField()),
                ('cpeak', models.FloatField()),
                ('peak', models.FloatField()),
                ('xcpeak', models.IntegerField()),
                ('ycpeak', models.IntegerField()),
                ('xpeak', models.IntegerField()),
                ('ypeak', models.IntegerField()),
                ('flag', models.IntegerField()),
                ('isDeleted', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TransientCandidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ra', models.FloatField()),
                ('dec', models.FloatField()),
                ('x_pix', models.IntegerField()),
                ('y_pix', models.IntegerField()),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('filename', models.CharField(max_length=100)),
                ('object_id', models.IntegerField()),
                ('slug', models.SlugField(max_length=110)),
                ('refImg', stdimage.models.StdImageField(upload_to='winnow_cutouts')),
                ('origImg', stdimage.models.StdImageField(upload_to='winnow_cutouts')),
                ('subtImg', stdimage.models.StdImageField(upload_to='winnow_cutouts')),
                ('mag_orig', models.FloatField(default=0.0, null=True)),
                ('mag_ref', models.FloatField(default=0.0, null=True)),
                ('mag_subt', models.FloatField(default=0.0, null=True)),
                ('isDeleted', models.IntegerField(default=0)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='winnow.Dataset')),
            ],
        ),
        migrations.AddField(
            model_name='sepinfo',
            name='trans_candidate',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='winnow.TransientCandidate'),
        ),
        migrations.AddField(
            model_name='ranking',
            name='trans_candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='winnow.TransientCandidate'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='features',
            field=models.ManyToManyField(to='winnow.Feature'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
