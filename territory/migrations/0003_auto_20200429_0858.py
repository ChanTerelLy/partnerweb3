# Generated by Django 2.2.1 on 2020-04-29 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('territory', '0002_promoutingreport'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promouter',
            name='area',
        ),
        migrations.AddField(
            model_name='promouter',
            name='area',
            field=models.ManyToManyField(to='territory.Area'),
        ),
    ]
