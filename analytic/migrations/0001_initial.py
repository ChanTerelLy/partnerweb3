# Generated by Django 2.2.1 on 2020-06-05 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('territory', '0003_auto_20200429_0858'),
        ('tickets_handler', '0030_aup'),
    ]

    operations = [
        migrations.CreateModel(
            name='MOZSales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_number', models.IntegerField()),
                ('creation_date', models.DateTimeField()),
                ('switched_date', models.DateField()),
                ('tariff', models.CharField(max_length=250)),
                ('moving', models.BooleanField()),
                ('conv_segment', models.CharField(max_length=200)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='territory.Address')),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets_handler.Workers')),
            ],
        ),
    ]
