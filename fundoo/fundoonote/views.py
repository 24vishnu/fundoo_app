"""
views.py: In views.py file we implement the all required view api,s
    Implement CRUD operation for FundooNote and Label
    ==============================
    CREATE --> POST -- Make New
    RETRIEVE --> GET -- List/ Search
    UPDATE --> PUT/PATCH -- Edit
    DELETE --> DELETE -- Delete
    ==============================

author : vishnu kumar
date : 12/10/2019
"""

import json
import pdb
import time
from datetime import datetime

from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from userlogin.services import util as servicesnote
import redis
from .models import Label, FundooNote
from .serializers import LabelSerializer, NotesSerializer, NoteShareSerializer

redis_db = redis.StrictRedis(host="localhost", db=0, port=6379)


class FundooLabelCreate(GenericAPIView):
    serializer_class = LabelSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request: request for create label
        :return: smd response
        """
        try:
            user = request.user
            name = request.data["name"]
            label = Label.objects.create(name=name, user_id=user.id)
            label.save()
            redis_db.hmset(str(user.id) + 'label', {label.pk: label.name})
            response = servicesnote.smd_response(True, 'You are successfully saved', [], status.HTTP_201_CREATED)
        except Exception as e:
            response = servicesnote.smd_response(False, str(e), [], status.HTTP_404_NOT_FOUND)
        return response

    def get(self, request):
        """
        :param request: client request for get label
        :return: return required response
        """
        try:
            user_redis_labels = redis_db.hvals(request.user.id)

            if len(user_redis_labels) < 1:
                get_label = Label.objects.filter(user_id=request.user.id)

                for x in range(len(get_label)):
                    print(str(request.user.id) + 'label',
                          {get_label.values()[x]['id']: get_label.values()[x]['name']})
                    redis_db.hmset((str(request.user.id) + 'label'),
                                   {get_label.values()[x]['id']: get_label.values()[x]['name']})
                user_redis_labels = redis_db.hvals(str(request.user.id) + 'label')

            response = servicesnote.smd_response(True, 'following is your label', [user_redis_labels],
                                                 status.HTTP_200_OK)
        except Exception as e:
            response = servicesnote.smd_response(False, str(e), [], status.HTTP_404_NOT_FOUND)
        return response


class FundooLabelDelete(GenericAPIView):
    serializer_class = LabelSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, label_id):
        """
        :param label_id: get label by label_id
        :param request: client request for get label
        :return: return required response

        """
        try:
            if redis_db.hexists(str(request.user.id)+'label', label_id) != 0:
                response = servicesnote.smd_response(True, 'following is your label',
                                                     [redis_db.hget(request.user.id, label_id)], status.HTTP_200_OK)
            else:
                response = servicesnote.smd_response(False, 'label does exist', [], status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = servicesnote.smd_response(False, str(e), [None], status.HTTP_404_NOT_FOUND)
        return response

    def delete(self, request, label_id):
        """
        :param request: client request for delete label
        :param label_id: delete by label id
        :return: return response
        """
        try:
            result = redis_db.hdel(request.user.id, label_id)
            if result != 0:
                get_label = Label.objects.get(id=label_id, user_id=request.user.id)
                get_label.delete()
                response = servicesnote.smd_response(True, 'note is successfully deleted', [],
                                                     status.HTTP_204_NO_CONTENT)
            else:
                response = servicesnote.smd_response(False, 'Label does not exist in database', [],
                                                     status.HTTP_400_BAD_REQUEST)

        except Label.DoesNotExist as e:
            response = servicesnote.smd_response(False, str(e), [], status.HTTP_404_NOT_FOUND)
        return response

    def put(self, request, label_id):
        """
        :param request: client request for delete label
        :param label_id: delete by label id
        :return: return response
        """
        global response
        put_serializer = LabelSerializer(data=request.data)
        try:
            get_label = Label.objects.get(id=label_id, user_id=request.user.id)
            if get_label is not None:
                if put_serializer.is_valid():
                    get_label.name = put_serializer.data['name']
                    get_label.save()
                    response = servicesnote.smd_response(True, 'Updated', [], status.HTTP_200_OK)
            else:
                response = servicesnote.smd_response(False, 'label not valid', [], status.HTTP_400_BAD_REQUEST)
        except Label.DoesNotExist as e:
            response = servicesnote.smd_response(False, str(e), [], status.HTTP_404_NOT_FOUND)
        return response


class FundooNoteCreate(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request: user request for create fundoo note
        :return: smd response
        """
        note_data = NotesSerializer(data=request.data, partial=True)
        try:

            labels = note_data.initial_data['label']
            note_data.initial_data['label'] = [Label.objects.get(name=x).id
                                               if Label.objects.filter(name=x).exists()
                                               else "Label not exist" for x in labels]
            collaborate = note_data.initial_data['collaborate']
            user = request.user
            note_data.initial_data['collaborate'] = [User.objects.get(email=x).id if
                                                     User.objects.filter(email=x).exists() and
                                                     x != User.objects.get(id=user.id).email
                                                     else "For collaborate user not exist" for x in collaborate]

            # print(note_data.initial_data['collaborate'])
            if note_data.is_valid():

                note_data.save(user_id=user.id)
                x = FundooNote.objects.filter(user_id=user.id)
                print('==========================================')
                for n in range(len(x)):
                    if redis_db.hexists(str(x[n].id)+'note', x[n].id) == 0:
                        continue
                    else:
                        redis_db.hmset(str(user.id) + 'note', {x[n].id: note_data.data})
                print('==========================================')
                response = servicesnote.smd_response(True, 'Your note is successfully created', [],
                                                     status.HTTP_201_CREATED)
                # return Response(response)
            else:
                response = servicesnote.smd_response(False, 'something is wrong',
                                                     ['Please enter correct ' + str(
                                                         [x for x in note_data.errors.keys()])],
                                                     status.HTTP_400_BAD_REQUEST)
        except KeyError as p:
            response = servicesnote.smd_response(False, str(p), [], status.HTTP_404_NOT_FOUND)
        return response

    def get(self, request):
        """
        :param request: user request for fetching all notes created by requested user
        :return: smd response
        """
        t2 = datetime.now()
        try:
            user_redis_note = redis_db.hvals(str(request.user.id) + 'note')
            # print('+++++', user_redis_note)
            if len(user_redis_note) < 1:
                get_note = FundooNote.objects.filter(user_id=request.user.id)
                note_data = NotesSerializer(get_note, many=True)
                for i in range(len(note_data.data)):
                    # print(note_data.data[i])
                    note_data.data[i]['label'] = [Label.objects.get(id=x).name
                                                  for x in note_data.data[i]['label']]
                    note_data.data[i]['collaborate'] = [User.objects.get(id=x).email
                                                        for x in note_data.data[i]['collaborate']]

                i = 0
                for n in note_data.data:
                    print({get_note.values()[i]['id']: [x for x in
                                                        n.values()]})
                    i += 1
                    redis_db.hmset(str(request.user.id) + 'note',
                                   {get_note.values()[i]['id']: {k: v for k, v in n.items()}})
                user_redis_note = redis_db.hvals(str(request.user.id) + 'note')

            response = servicesnote.smd_response(True, 'following is your created note',
                                                 ['time: ' + str(datetime.now() - t2), user_redis_note],
                                                 status.HTTP_200_OK)
        except Exception as e:
            response = servicesnote.smd_response(False, str(e), [], status.HTTP_404_NOT_FOUND)
        return response


class FundooNoteModification(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, note_id):
        """
        :param note_id: get note using note id
        :param request: user request for fetching all notes created by requested user
        :return: smd response
        """
        t1 = time.time()
        try:
            # get_note = FundooNote.objects.filter(id=note_id, user_id=request.user.id)
            # note_data = NotesSerializer(get_note, many=True)
            #
            # # print(note_data.data[0]['label'])
            # # print(note_data.data[0]['collaborate'])
            # if len(note_data.data) > 0:
            #     note_data.data[0]['label'] = [Label.objects.get(id=x).name
            #                                   for x in note_data.data[0]['label']]
            #     note_data.data[0]['collaborate'] = [User.objects.get(id=x).email
            #                                         for x in note_data.data[0]['collaborate']]

            user_redis_note = redis_db.hvals(str(request.user.id)+'note')
            print('+++++', user_redis_note)
            if len(user_redis_note) < 1:
                get_note = FundooNote.objects.filter(id=note_id, user_id=request.user.id)
                note_data = NotesSerializer(get_note, many=True)
                print(get_note.values())
                print('---------------')
                print(note_data.data)
                # for x in range(len(get_label)):
                #     redis_db.hmset(request.user.id, {get_label.values()[x]['id']: get_label.values()[x]['name']})
                # user_redis_note = redis_db.hvals(request.user.id)

                response = servicesnote.smd_response(True, 'following is your created note',
                                                     ['time: ' + str(time.time() - t1), note_data.data],
                                                     status.HTTP_200_OK)
            else:
                response = servicesnote.smd_response(False, 'note does not exist', [],
                                                     status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = servicesnote.smd_response(False, str(e), [], status.HTTP_404_NOT_FOUND)
        return response

    def delete(self, request, note_id):
        """
        :param request: request for delete the note created by authenticated user
        :param note_id: check credentials by note_id
        :return: return response
        """
        try:
            get_label = FundooNote.objects.get(id=note_id, user_id=request.user.id)
            get_label.delete()
            response = servicesnote.smd_response(True, 'note is successfully deleted', [], status.HTTP_204_NO_CONTENT)
        except FundooNote.DoesNotExist as e:
            response = servicesnote.smd_response(False, str(e), [], status.HTTP_404_NOT_FOUND)
        return response

    def put(self, request, note_id):
        """
        :param request:  data is requested
        :param note_id:  note id
        :return: will fetch note id from database
        """
        try:
            # data is fetched from user
            # pdb.set_trace()
            instance = FundooNote.objects.get(id=note_id)
            data = request.data
            try:
                data["label"] = [Label.objects.get(name=name).id for name in data["label"]]
                print(data['label'])
            except KeyError:
                pass
            try:
                data["collaborate"] = [User.objects.get(email=email).id for email in data["collaborate"]]
                print(data['collaborate'])
            except KeyError:
                pass
            serializer = NotesSerializer(instance, data=data, partial=True)
            # here serialized data checked for validation and saved
            if serializer.is_valid():
                # note_create = serializer.save()
                serializer.save()
                response = servicesnote.smd_response(True, 'note created', [], status.HTTP_201_CREATED)
            else:
                response = servicesnote.smd_response(True, 'note was not created', [], status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = servicesnote.smd_response(True, str(e), [], status.HTTP_404_NOT_FOUND)
        return response


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        content = {'messege': 'Hello world'}
        return Response(content)


class ShareNote(GenericAPIView):
    """
    Share Note API is used for share our note with note title and note content on social network
    """
    serializer_class = NoteShareSerializer

    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request: request parameter use for get data of Note like note title and note content
        :return: if note is not empty then render on share page
        """

        try:
            note_data = NoteShareSerializer(data=request.data)
            if note_data.is_valid():
                context = {
                    'title': note_data.data['title'],
                    'content': note_data.data['content'],
                    'domain': request.build_absolute_uri
                }
                response = servicesnote.smd_response(True, 'share your note successfully',
                                                     [request.build_absolute_uri],
                                                     status.HTTP_200_OK)
                return render(request, 'home.html', context)
            else:
                response = servicesnote.smd_response(False, 'something is wrong', [],
                                                     status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = servicesnote.smd_response(False, str(e), [], status.HTTP_404_NOT_FOUND)
        return response
