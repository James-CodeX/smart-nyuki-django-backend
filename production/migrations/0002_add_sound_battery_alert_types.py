# Generated by Django 5.2.1 on 2025-07-15 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alerts',
            name='alert_type',
            field=models.CharField(choices=[('Temperature', 'Temperature'), ('Humidity', 'Humidity'), ('Weight', 'Weight'), ('Sound', 'Sound'), ('Battery', 'Battery'), ('Inspection_Due', 'Inspection Due'), ('Pest_Risk', 'Pest Risk'), ('Swarm_Risk', 'Swarm Risk')], max_length=20),
        ),
    ]
