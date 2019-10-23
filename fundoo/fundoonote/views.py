import json

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Label
from .serializers import FileSerializer, LabelSerializer, LabelModifySerializer


class FundooLabelCreate(GenericAPIView):
    serializer_class = LabelSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        label_serializer = LabelSerializer(data=request.data)
        try:
            if label_serializer.is_valid():
                label_serializer.save()
        except Exception as e:
            return HttpResponse('exception', str(e))
        return HttpResponse('OK')


class FundooLabelDelete(GenericAPIView):
    serializer_class = LabelModifySerializer

    def delete(self, request, name):
        smd = {"success": True, "message": "note is deleted", "data": []}
        try:
            lab = Label.objects.get(name=name)
            lab.delete()
        except Label.DoesNotExist as e:
            print('1')
            smd['message'] = str(e)
        return HttpResponse(json.dumps(smd))

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
            print("1", file_serialize.get_fields().values())
            print(file_serialize.data.values())
            return Response(file_serialize.data['file_details'], status=status.HTTP_201_CREATED)
        else:
            return Response(file_serialize.errors, status=status.HTTP_400_BAD_REQUEST)
