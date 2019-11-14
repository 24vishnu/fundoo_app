"""fundoo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view

from userlogin import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
schema_view = get_swagger_view(title='My API')


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/user', include('userlogin.urls')),
    path('', include('userlogin.urls')),
    # path('accounts/', include('allauth.urls')),
    path("sociallogin/", views.social_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # path('socialauth/', include('social_django.urls', namespace="social")),
    path("", views.home, name="home"),
    path('swagger', schema_view),
    path('api/', include('fundoonote.urls')),
]


