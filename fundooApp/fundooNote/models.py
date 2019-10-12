from django.db import models


class ImageUpload(models.Model):
    file_details = models.FileField(blank=False, null=False)

    def __str__(self):
        return str(self.file_details)


class Note(models.Model):
    note_title = models.CharField(max_length=100)
    note_body = models.TextField(max_length=100)
    note_timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    note_update = models.DateTimeField(auto_now=True, auto_now_add=False)

    # image_upload = models.ImageField(blank=False, null=False)
    # note_file = models.FileField()
    # note_pin = models.BooleanField(default=False)
    # note_archive = models.BooleanField(default=False)  # if true then hide the note
    # note_collaborate = models.EmailField(max_length=150, null=False)
    # note_delete = models.SlugField()

    def __str__(self):
        return str(self.note_title)
