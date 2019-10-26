from rest_framework import serializers
from .models import ExtendUser, Label, FundooNote


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendUser
        fields = ['file_details']


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['name']


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundooNote
        fields = ['title', 'note', 'label', 'url', 'archive', 'coll', 'image', 'reminder']
