# Generated by Django 4.2.1 on 2023-08-19 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0024_remove_product_is_admin_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.DecimalField(decimal_places=2, default=10, max_digits=10),
        ),
    ]
