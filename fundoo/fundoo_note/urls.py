from django.conf.urls import url

from .views import HelloView, ImageView

app_name = 'fundoo_note'
urlpatterns = [
    url(r'^hello/', HelloView.as_view(), name='hello'),
    url(r'^upload/$', ImageView.as_view(), name='image-upload')
]