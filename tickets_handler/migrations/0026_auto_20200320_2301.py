# Generated by Django 2.2.1 on 2020-03-20 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_handler', '0025_acl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='building',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
