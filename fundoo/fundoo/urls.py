from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from userlogin import views

schema_view = get_swagger_view(title='My API')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('userlogin.urls')),
    path('accounts/', include('allauth.urls')),
    path("social_login/", views.social_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('social-auth/', include('social_django.urls', namespace="social")),
    path("", views.home, name="home"),

    path('note/', include('fundoonote.urls')),
]

