# Generated by Django 4.2.1 on 2023-08-14 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_alter_customer_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_admin_product',
            field=models.BooleanField(default=False),
        ),
    ]
