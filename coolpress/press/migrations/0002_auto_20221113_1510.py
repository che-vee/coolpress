# Generated by Django 3.2.7 on 2022-11-13 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('press', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cooluser',
            name='github_repos',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='image_link',
            field=models.URLField(blank=True, null=True),
        ),
    ]