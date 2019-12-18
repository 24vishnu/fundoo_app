from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from rest_framework_swagger.views import get_swagger_view

from .views import (
    LabelList,
    LabelDetails,
    NoteList,
    NoteDetails,
    ShareNote,
    Reminders,
    NoteArchive,
    NoteTrashed,
    PaginationApiView,
    PaginationAPI,
    LabelNotesDetails,
    ElasticSearchAPI
)

SCHEMA_VIEW = get_swagger_view(title='Fundoo API')

app_name = 'fundoonote'
urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('labels/', LabelList.as_view(), name='label_list'),
    path('label/<label_id>', LabelDetails.as_view(), name='label_details'),
    path('notes/', NoteList.as_view(), name='note_list'),
    path('note/<note_id>', NoteDetails.as_view(), name='note_details'),
    path('reminders/', Reminders.as_view(), name='note_reminder'),
    path('archives/', NoteArchive.as_view(), name='note_archive'),
    path('trashed/', NoteTrashed.as_view(), name='note_trashed'),
    path('pagination/', PaginationApiView.as_view(), name='pagination'),
    path('share/', ShareNote.as_view(), name='note_share'),
    path('paginationrest/', PaginationAPI.as_view(), name='rest_pagination'),
    path('labelnote/<label_id>', LabelNotesDetails.as_view(), name='notes_of_label'),
    path('elasticsearch/<query_data>', ElasticSearchAPI.as_view(), name='search_engine'),
]

urlpatterns += staticfiles_urlpatterns()
