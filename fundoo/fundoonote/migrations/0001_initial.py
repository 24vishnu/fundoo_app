# Generated by Django 2.2.7 on 2019-11-09 10:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('user', models.ForeignKey(default='admin', on_delete=django.db.models.deletion.CASCADE, related_name='label_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FundooNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.CharField(max_length=500)),
                ('image', models.ImageField(blank=True, max_length=500, null=True, upload_to='image')),
                ('is_archive', models.BooleanField(default=False, verbose_name='archived')),
                ('is_trashed', models.BooleanField(default=False, verbose_name='delete')),
                ('is_check', models.BooleanField(default=False, verbose_name='check box')),
                ('is_pin', models.BooleanField(default=False)),
                ('reminder', models.DateTimeField(blank=True, null=True)),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('collaborate', models.ManyToManyField(blank=True, related_name='collaborate', to=settings.AUTH_USER_MODEL)),
                ('label', models.ManyToManyField(blank=True, related_name='label', to='fundoonote.Label')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
