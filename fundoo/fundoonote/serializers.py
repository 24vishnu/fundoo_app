from rest_framework import serializers
from .models import Label, FundooNote


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['name']


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundooNote
        fields = ['title', 'content', 'label', 'is_archive', 'is_trashed', 'collaborate', 'image', 'reminder']


class NoteShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundooNote
        fields = ['title', 'content']
