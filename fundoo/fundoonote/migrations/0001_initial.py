# Generated by Django 2.2.6 on 2019-10-23 09:23

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
            name='ExtendUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_details', models.FileField(upload_to='')),
            ],
        ),
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
                ('title', models.CharField(blank=True, max_length=100)),
                ('note', models.CharField(max_length=500)),
                ('image', models.ImageField(blank=True, max_length=500, null=True, upload_to='image')),
                ('archive', models.BooleanField(default=False, verbose_name='is_archived')),
                ('delete_note', models.BooleanField(default=False, verbose_name='delete_note')),
                ('copy', models.BooleanField(default=False, verbose_name='make a copy')),
                ('checkbox', models.BooleanField(default=False, verbose_name='check box')),
                ('pin', models.BooleanField(default=False)),
                ('url', models.URLField(blank=True)),
                ('coll', models.ManyToManyField(blank=True, related_name='coll', to=settings.AUTH_USER_MODEL)),
                ('label', models.ManyToManyField(blank=True, related_name='label', to='fundooNote.Label')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
