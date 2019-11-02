from django.contrib import admin
from .models import ImageUpload, UserProfile

# Register your models here.
admin.site.register(ImageUpload)
admin.site.register(UserProfile)
