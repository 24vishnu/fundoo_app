from rest_framework_simplejwt import views as jwt_views
from django.conf.urls import url
from django.urls import path

from .views import (
    ImageView,
    FundooLabelCreate,
    FundooLabelDelete
)

app_name = 'fundoonote'
urlpatterns = [
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^upload/$', ImageView.as_view(), name='image-upload'),
    url(r'^label/$', FundooLabelCreate.as_view(), name='label'),
    path('delete/<id>/', FundooLabelDelete.as_view(), name='label_delete'),

]