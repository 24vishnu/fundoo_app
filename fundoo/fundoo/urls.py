from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_simplejwt import views as jwt_views
from rest_framework_swagger.views import get_swagger_view

from fundoo_note.views import FilePolicyAPI

schema_view = get_swagger_view(title='My API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('authenticate/', include('login_app.urls')),
    # path('note/', include('fundoo_note.urls')),
    url(r'^upload/$', TemplateView.as_view(template_name='upload.html'), name='upload-home'),
    url(r'^api/files/policy/$', FilePolicyAPI.as_view(), name='upload-policy'),
]

