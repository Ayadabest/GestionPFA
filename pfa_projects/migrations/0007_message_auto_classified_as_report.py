# Generated by Django 5.2.3 on 2025-06-24 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pfa_projects', '0006_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='auto_classified_as_report',
            field=models.BooleanField(default=False),
        ),
    ]
