from django.conf.urls import url
from django.urls import path

from .views import (
                note_create,
                note_list,
                note_update,
                note_delete,
                note_detail,
                ImageView,
                FundooLabelCreate,
                FundooLabelDelete
                )

app_name = 'fundooNote'
urlpatterns = [
    url(r'^create/$', note_create, name='note_create'),
    url(r'^list/$',  note_list, name='note_list'),
    url(r'^update/$', note_update, name='note_update'),
    url(r'^detail/$', note_detail, name='note_detail'),

    url(r'^upload/$', ImageView.as_view(), name='image-upload'),
    url(r'^label/$', FundooLabelCreate.as_view(), name='label'),
    path('delete/<name>/', FundooLabelDelete.as_view(), name='label_delete'),
]
