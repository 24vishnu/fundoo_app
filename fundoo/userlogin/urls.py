from django.conf.urls import url
from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from . import views

SCHEMA_VIEW = get_swagger_view(title='Fundoo API')

app_name = 'userlogin'

urlpatterns = [
    url(r'^signup/$', views.UserRegistration.as_view(), name='sign_up'),
    path('login/', views.UserLogin.as_view(), name='login'),
    path('user/', views.Profile.as_view(), name="Profile"),
    path('upload/', views.Upload.as_view(), name="upload"),
    path('update/<image_id>', views.ImageUpdate.as_view(), name="update"),
    path('forgotpassword/', views.ForgotPassword.as_view(), name='forgotpassword'),
    path('resetpassword/<token>/', views.ResetPassword.as_view(), name='resetpassword'),
    path('login/activate/<token>/', views.activate, name='activate'),
    # url('', SCHEMA_VIEW),
]
