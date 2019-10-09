from django.db import models


class ImageUpload(models.Model):
    file_details = models.FileField(blank=False, null=False)

    def __str__(self):
        return str(self.file_details)
