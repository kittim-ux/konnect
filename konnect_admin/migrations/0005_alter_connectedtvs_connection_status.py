# Generated by Django 4.1.5 on 2023-01-21 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('konnect_admin', '0004_alter_connectedtvs_connection_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectedtvs',
            name='connection_status',
            field=models.CharField(max_length=255),
        ),
    ]
