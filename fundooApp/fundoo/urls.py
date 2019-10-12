from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
# from allauth.account import views
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth import views as auth_views
from userlogin import views
schema_view = get_swagger_view(title='My API')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('userlogin.urls')),
    path('accounts/', include('allauth.urls')),
    path("login/", views.login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('social-auth/', include('social_django.urls', namespace="social")),
    path("", views.home, name="home"),

    path('note/', include('fundooNote.urls')),
]

