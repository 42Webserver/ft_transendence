# Generated by Django 4.2.15 on 2024-11-12 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_userprofile_otp_secret'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='verified_2fa',
            field=models.BooleanField(default=False),
        ),
    ]