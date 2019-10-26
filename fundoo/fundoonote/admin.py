from django.contrib import admin

from .models import FundooNote, Label


class NoteModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'note', 'archive']
    list_display_links = ['title']
    list_editable = ['note']
    list_filter = ['archive', 'note']

    class Meta:
        model = FundooNote


admin.site.register(Label)
admin.site.register(FundooNote, NoteModelAdmin)
