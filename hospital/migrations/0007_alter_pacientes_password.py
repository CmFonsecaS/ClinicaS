# Generated by Django 5.0.3 on 2024-05-04 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0006_remove_reservamedica_prescripcion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pacientes',
            name='password',
            field=models.CharField(max_length=50),
        ),
    ]
