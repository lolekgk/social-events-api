# Generated by Django 4.1.5 on 2023-02-19 15:35

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0005_location_latitude_location_longitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='events.location'),
        ),
        migrations.AlterField(
            model_name='location',
            name='latitude',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)]),
        ),
        migrations.AlterField(
            model_name='location',
            name='longitude',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)]),
        ),
        migrations.CreateModel(
            name='EventInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('A', 'Accepted'), ('D', 'Declined'), ('P', 'Pending')], default='P', max_length=1)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invited_users', to='events.event')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_invitations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
