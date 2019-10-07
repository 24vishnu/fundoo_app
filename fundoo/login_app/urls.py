from django.conf.urls import url
from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from . import views

SCHEMA_VIEW = get_swagger_view(title='Fundoo API')

app_name = 'login_app'

urlpatterns = [
    url(r'^SignUp/$', views.UserRegistration.as_view(), name='sign_up'),
    path('SignIn/', views.UserLogin.as_view(), name='sign_in'),
    path('UserProfile', views.UserProfile.as_view(), name="Profile"),
    path('ForgotPassword/', views.ForgotPassword.as_view(), name='forgot_password'),
    path('ResetPassword/', views.ResetPassword.as_view(), name='reset_password'),
    path('login/activate/<token>/', views.activate, name='activate'),
    url('auth/', SCHEMA_VIEW),
]
