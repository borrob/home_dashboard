# Generated by Django 2.0.2 on 2018-03-05 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Meter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meter_name', models.CharField(max_length=30)),
                ('meter_unit', models.CharField(max_length=10)),
            ],
        ),
    ]
