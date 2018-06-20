# Generated by Django 2.0.6 on 2018-06-20 15:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0007_booking_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='check_in_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='booking',
            name='number_of_tickets',
            field=models.IntegerField(blank=True, default=0, validators=[django.core.validators.MinValueValidator(1, 'Mindestens ein Ticket'), django.core.validators.MaxValueValidator(8, 'Maximal 8 Tickets pro Buchung erlaubt')]),
        ),
    ]