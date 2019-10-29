from django.contrib import admin

from .models import FundooNote, Label


class NoteModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'is_archive']
    list_display_links = ['title']
    # list_editable = ['content']
    list_filter = ['is_archive', 'content']

    class Meta:
        model = FundooNote


admin.site.register(Label)
admin.site.register(FundooNote, NoteModelAdmin)