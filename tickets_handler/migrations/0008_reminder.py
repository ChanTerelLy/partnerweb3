# Generated by Django 2.2.1 on 2020-02-13 21:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_handler', '0007_employer_profile_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_number', models.TextField()),
                ('client_name', models.TextField()),
                ('client_number', models.CharField(max_length=10)),
                ('timer', models.DateTimeField()),
                ('link', models.URLField(blank=True, null=True)),
                ('recipient', models.TextField()),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets_handler.Workers')),
            ],
        ),
    ]