# Generated by Django 2.2.1 on 2020-03-31 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('territory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoutingReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('agent', models.CharField(max_length=100)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='territory.Address')),
            ],
        ),
    ]
