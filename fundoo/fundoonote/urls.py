from rest_framework_simplejwt import views as jwt_views
from django.conf.urls import url
from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from .views import (
    FundooLabelCreate,
    FundooLabelDelete,
    FundooNoteCreate,
    FundooNoteModification,
    ShareNote,
)


SCHEMA_VIEW = get_swagger_view(title='Fundoo API')

app_name = 'fundoonote'
urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^label/$', FundooLabelCreate.as_view(), name='label_define'),
    path('label/<label_id>/', FundooLabelDelete.as_view(), name='label_alter'),
    path('note/', FundooNoteCreate.as_view(), name='note_define'),
    path('note/<note_id>/', FundooNoteModification.as_view(), name='note_alter'),
    path('share/', ShareNote.as_view(), name='note_share'),
    # url('note/', SCHEMA_VIEW),
]
