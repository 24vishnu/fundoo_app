"""
models.py
    class for define some model classes as requirement

author : vishnu kumar
date : 29/09/2019
"""
from django.contrib.auth.models import User
from django.db import models


class ImageUpload(models.Model):
    file_details = models.FileField(blank=False, null=False)

    def __str__(self):
        return str(self.file_details)


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField()

    def __str__(self):
        return self.user.email
