# Generated by Django 5.1.5 on 2025-02-11 14:36

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0002_remove_document_owner_document_access_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
