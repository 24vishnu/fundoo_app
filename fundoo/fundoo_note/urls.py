from django.conf.urls import url
from django.views.generic.base import TemplateView
from .views import FilePolicyAPI

app_name = 'fundoo_note'
urlpatterns = [

    url(r'^upload/$', TemplateView.as_view(template_name='upload.html'), name='upload-home'),
    url(r'^api/files/policy/$', FilePolicyAPI.as_view(), name='upload-policy'),
]