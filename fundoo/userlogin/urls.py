from django.conf.urls import url
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view

from . import views

SCHEMA_VIEW = get_swagger_view(title='Fundoo API')

app_name = 'userlogin'

urlpatterns = [
    url(r'^signup/$', views.UserRegistration.as_view(), name='sign_up'),
    path('login/', views.UserLogin.as_view(), name='sign_in'),
    path('user/', views.UserProfile.as_view(), name="Profile"),
    path('upload/', views.Upload.as_view(), name="upload"),
    path('share_note/', views.ShareNote.as_view(), name="share"),
    path('forgot_password/', views.ForgotPassword.as_view(), name='forgot_password'),
    path('reset_password/<token>/', views.ResetPassword.as_view(), name='reset_password'),
    path('login/activate/<token>/', views.activate, name='activate'),
    url('', SCHEMA_VIEW),
]
