from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FileSerializer


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        content = {'messege': 'Hello world'}
        return Response(content)


class ImageView(GenericAPIView):
    serializer_class = FileSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        file_serialize = FileSerializer(data=request.FILES)
        if file_serialize.is_valid():
            file_serialize.save()
            print("1",file_serialize.get_fields().values())
            print(file_serialize.data.values())
            return Response(file_serialize.data['file_details'], status=status.HTTP_201_CREATED)
        else:
            return Response(file_serialize.errors, status=status.HTTP_400_BAD_REQUEST)
