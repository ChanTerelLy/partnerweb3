# Generated by Django 3.0.2 on 2020-02-08 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_handler', '0003_ticketprice'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.IntegerField(max_length=10)),
                ('position', models.TextField()),
            ],
        ),
    ]
