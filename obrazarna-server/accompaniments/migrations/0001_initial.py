# Generated by Django 4.0.4 on 2022-05-30 06:45

import common.uploads
from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accompaniment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=200, verbose_name='Název')),
                ('author', models.CharField(max_length=200, verbose_name='Autor')),
                ('file', models.FileField(help_text='MP3 (?) soubor, max 10 vteřin dlouhý; kvalita?', max_length=255, upload_to=common.uploads.UploadPath('accompaniments'), verbose_name='Soubor')),
            ],
            options={
                'verbose_name': 'Doprovod',
                'verbose_name_plural': 'Doprovody',
                'ordering': ['title'],
            },
        ),
    ]
