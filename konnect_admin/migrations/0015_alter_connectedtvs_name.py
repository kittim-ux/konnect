# Generated by Django 4.1.5 on 2023-01-29 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('konnect_admin', '0014_remove_connectedtvs_tech_support_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectedtvs',
            name='name',
            field=models.CharField(default='null', max_length=255),
        ),
    ]
