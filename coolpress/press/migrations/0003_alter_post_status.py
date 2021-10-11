# Generated by Django 3.2.7 on 2021-10-08 15:46

from django.db import migrations, models
import press.models


class Migration(migrations.Migration):

    dependencies = [
        ('press', '0002_auto_20211005_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('PUBLISHED', 'Published post')], default=press.models.PostStatus['DRAFT'], max_length=32),
        ),
    ]