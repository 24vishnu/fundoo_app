from django.contrib import admin

from .models import Note


class NoteModelAdmin(admin.ModelAdmin):
    list_display = ['note_title', 'note_update', 'note_timestamp']
    list_display_links = ['note_update']
    list_editable = ['note_title']
    list_filter = ['note_update', 'note_timestamp']
    search_fields = ['note_title', 'note_body']

    class Meta:
        model = Note


admin.site.register(Note, NoteModelAdmin)
