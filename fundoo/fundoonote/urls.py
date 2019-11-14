from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from rest_framework_swagger.views import get_swagger_view

from .views import (
    LabelCreate,
    LabelDelete,
    NoteCreate,
    NoteModification,
    ShareNote,
    Reminders,
    NoteArchive,
    NoteTrashed,
    PaginationApiView,
    PaginationAPI,
)

SCHEMA_VIEW = get_swagger_view(title='Fundoo API')

app_name = 'fundoonote'
urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^labels/$', LabelCreate.as_view(), name='label_define'),
    path('label/<label_id>/', LabelDelete.as_view(), name='label_alter'),
    path('notes/', NoteCreate.as_view(), name='note_define'),
    path('note/<note_id>/', NoteModification.as_view(), name='note_alter'),
    path('reminders/', Reminders.as_view(), name='note_reminder'),
    path('archives/', NoteArchive.as_view(), name='note_archive'),
    path('trashed/', NoteTrashed.as_view(), name='note_archive'),
    path('pagination/', PaginationApiView.as_view(), name='pagination'),
    path('share/', ShareNote.as_view(), name='note_share'),
    path('paginationrest/', PaginationAPI.as_view(), name='rest_api'),
    # url('note/', SCHEMA_VIEW),
]

urlpatterns += staticfiles_urlpatterns()