# Generated by Django 4.2.1 on 2023-05-23 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_rename_created_at_product_ahmet'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='ahmet',
            new_name='created_at',
        ),
    ]
