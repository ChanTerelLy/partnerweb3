# Generated by Django 2.2.1 on 2020-02-19 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_handler', '0013_area_promouter'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=70)),
                ('entrance', models.IntegerField()),
                ('flats', models.IntegerField()),
                ('entrance_img', models.ImageField(upload_to='')),
                ('flats_img', models.ImageField(upload_to='')),
            ],
        ),
    ]