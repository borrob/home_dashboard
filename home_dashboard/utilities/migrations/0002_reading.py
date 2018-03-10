# Generated by Django 2.0.2 on 2018-03-10 19:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('reading', models.DecimalField(decimal_places=2, max_digits=10)),
                ('remark', models.CharField(max_length=255)),
                ('meter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utilities.Meter')),
            ],
        ),
    ]
