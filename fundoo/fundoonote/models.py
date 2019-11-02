from django.contrib.auth.models import User, AbstractUser
from django.db import models


class Label(models.Model):

    name = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='label_user', default="admin")

    def __str__(self):
        return self.name


class FundooNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    title = models.CharField(max_length=100, blank=True)
    content = models.CharField(max_length=500, )
    image = models.ImageField(max_length=500, blank=True, null=True, upload_to="image")
    is_archive = models.BooleanField("archived", default=False)
    is_delete = models.BooleanField("delete", default=False)
    label = models.ManyToManyField(Label, related_name="label", blank=True)
    collaborate = models.ManyToManyField(User, related_name='collaborate', blank=True)
    is_check = models.BooleanField("check box", default=False)
    is_pin = models.BooleanField(default=False)
    reminder = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
