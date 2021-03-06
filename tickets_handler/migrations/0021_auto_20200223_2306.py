# Generated by Django 2.2.1 on 2020-02-23 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_handler', '0020_auto_20200223_2300'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressToDo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField(auto_now=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets_handler.Address')),
                ('to_promouter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets_handler.Promouter')),
            ],
        ),
        migrations.AlterField(
            model_name='addressdata',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets_handler.AddressToDo'),
        ),
    ]
