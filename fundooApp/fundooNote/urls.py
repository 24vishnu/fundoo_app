from django.conf.urls import url

from .views import (
                note_create,
                note_list,
                note_update,
                note_delete,
                note_detail,
                ImageView,
                )

app_name = 'fundooNote'
urlpatterns = [
    url(r'^create/$', note_create, name='note_create'),
    url(r'^list/$',  note_list, name='note_list'),
    url(r'^update/$', note_update, name='note_update'),
    url(r'^delete/$', note_delete, name='note_delete'),
    url(r'^detail/$', note_detail, name='note_detail'),
    url(r'^upload/$', ImageView.as_view(), name='image-upload'),
]