# Generated by Django 2.2 on 2019-09-13 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_handler', '0002_auto_20190913_1009'),
    ]

    operations = [
        migrations.AddField(
            model_name='workers',
            name='url',
            field=models.URLField(default='https://partnerweb.beeline.ru/partner/worker/'),
            preserve_default=False,
        ),
    ]
