# Generated by Django 5.1.5 on 2025-04-18 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='folder',
            name='name',
            field=models.TextField(),
        ),
    ]
