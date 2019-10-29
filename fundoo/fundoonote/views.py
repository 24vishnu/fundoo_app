import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from userlogin.services import util as servicesnote

from .models import Label, FundooNote
from .serializers import FileSerializer, LabelSerializer, NotesSerializer


class FundooLabelCreate(GenericAPIView):
    serializer_class = LabelSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user = request.user
            name = request.data["name"]
            label = Label.objects.create(name=name, user_id=user.id)
            label.save()
            response = servicesnote.smd_response(True, 'You are successfully saved', [])
        except Exception as e:
            response = servicesnote.smd_response(False, str(e), [])
        return Response(response)

    def get(self, request):
        global response
        try:
            get_label = Label.objects.filter(user_id=request.user.id)
            print()
            p = [get_label.values()[x]['name'] for x in range(len(get_label))]
            # q = [x[1] for x in get_label]
            print('-----------', p)
            # print('-----------', q)
            response = servicesnote.smd_response(True, 'following is your label', [p])
        except Exception as e:
            response = servicesnote.smd_response(False, str(e), [])
        return Response(response)


class FundooLabelDelete(GenericAPIView):
    serializer_class = LabelSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, id):
        try:
            get_label = Label.objects.get(id=id, user_id=request.user.id)

            get_label.delete()
            response = servicesnote.smd_response(True, 'note is successfully deleted', [])
        except Label.DoesNotExist as e:
            response = servicesnote.smd_response(False, str(e), [])
        return Response(response)

    def put(self, request, id):
        global response
        put_serializer = LabelSerializer(data=request.data)
        try:
            get_label = Label.objects.get(id=id, user_id=request.user.id)
            if get_label is not None:
                if put_serializer.is_valid():
                    get_label.name = put_serializer.data['name']
                    get_label.save()
                    response = servicesnote.smd_response(True, 'Updated', [])
            else:
                response = servicesnote.smd_response(False, 'label not valid', [])
        except Label.DoesNotExist as e:
            response = servicesnote.smd_response(False, str(e), [])
        return Response(response)


class FundooNoteCreate(GenericAPIView):
    serializer_class = NotesSerializer

    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        note_data = NotesSerializer(data=request.data, partial=True)
        try:

            labels = note_data.initial_data['label']
            note_data.initial_data['label'] = [Label.objects.get(name=x).id
                                               if Label.objects.filter(name=x).exists()
                                               else "Label not exist" for x in labels]
            collaborate = note_data.initial_data['collaborate']
            note_data.initial_data['collaborate'] = [User.objects.get(username=x).id if
                                                     User.objects.filter(username=x).exists()
                                                     else "For collaborate user not exist" for x in collaborate]

            print(note_data.initial_data)
            if note_data.is_valid():
                print('yes valid')
                user = request.user
                note_data.save(user_id=user.id)
                response = servicesnote.smd_response(True, 'Your note is successfully created', [])
                # return Response(response)
            else:
                print('Not valid')
                response = servicesnote.smd_response(True, note_data.errors, [])
        except KeyError as p:
            print('pppppp', p)
            response = servicesnote.smd_response(False, str(p), [])
        return Response(response)


class FundooNoteModification(GenericAPIView):
    pass


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