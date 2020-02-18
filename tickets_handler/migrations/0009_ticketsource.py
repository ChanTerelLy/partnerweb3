# Generated by Django 2.2.1 on 2020-02-15 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_handler', '0008_reminder'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_number', models.CharField(max_length=9)),
                ('source', models.CharField(max_length=50)),
            ],
        ),
    ]
