from rest_framework_simplejwt import views as jwt_views
from django.conf.urls import url
from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from .views import (
    ImageView,
    FundooLabelCreate,
    FundooLabelDelete,
    FundooNoteCreate,
)


SCHEMA_VIEW = get_swagger_view(title='Fundoo API')

app_name = 'fundoonote'
urlpatterns = [
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^upload/$', ImageView.as_view(), name='image-upload'),
    url(r'^label/$', FundooLabelCreate.as_view(), name='label'),
    path('delete/<id>/', FundooLabelDelete.as_view(), name='label_delete'),
    path('create_note/', FundooNoteCreate.as_view(), name='note'),
    url('', SCHEMA_VIEW),
]
