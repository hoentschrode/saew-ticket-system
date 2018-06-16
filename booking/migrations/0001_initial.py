# Generated by Django 2.0.6 on 2018-06-15 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateTimeField(auto_created=True)),
                ('email', models.EmailField(blank=True, default='', max_length=254)),
                ('number_of_tickets', models.IntegerField(blank=True, default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Performance title', max_length=200)),
                ('start', models.DateTimeField(help_text='Date and time of performance')),
                ('capacity', models.IntegerField(default=0, help_text='Maximum number of tickes')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='performance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.Performance'),
        ),
    ]
