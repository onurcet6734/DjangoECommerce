# Generated by Django 4.2.1 on 2023-07-27 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='ip',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
