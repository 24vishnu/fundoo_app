from rest_framework import serializers
from .models import ExtendUser, Label


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendUser
        fields = ['file_details']


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['name', 'user']


class LabelModifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['name', 'user']

