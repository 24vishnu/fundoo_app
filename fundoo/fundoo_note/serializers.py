from rest_framework import serializers
from .models import ImageUpload


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ['file_details']
