# Generated by Django 4.1.5 on 2023-01-28 22:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='friends',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, upload_to='user-profile-images/'),
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=255)),
                ('administrators', models.ManyToManyField(related_name='groups_admin', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='groups_member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]