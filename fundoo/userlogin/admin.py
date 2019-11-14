from django.contrib import admin

from .models import UserProfile


class NoteModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'image']
    list_display_links = ['user', 'image']

    class Meta:
        model = UserProfile


admin.site.register(UserProfile, NoteModelAdmin)
