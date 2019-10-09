from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth import views as auth_views
from userlogin import views
schema_view = get_swagger_view(title='My API')


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('as/', include('userlogin.urls')),
    # path('login/', ('allauth.urls')),
    url(r'^accounts/', include('allauth.urls')),
    path("login/", views.login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # path('social-auth/', include('social_django.urls', namespace="social")),
    path("", views.home, name="home"),

    # url(r'^doc/', include('fundooNote.urls')),
]


# if settings.DEBUG:
#   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

