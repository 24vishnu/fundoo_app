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
    path('accounts/', include('allauth.urls')),
    path("sociallogin/", views.social_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('socialauth/', include('social_django.urls', namespace="social")),
    path("", views.home, name="home"),
    path('swagger', schema_view),
    path('api/', include('fundoonote.urls')),
]

