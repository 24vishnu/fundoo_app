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
import ast
import json
import logging
import pdb
import time
from datetime import datetime

import simplejson
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from services import util as servicesnote
import redis

from fundoo.settings import file_handler
from fundoo.url_settings import r_db, redis_port
from .models import Label, FundooNote
from .serializers import LabelSerializer, NotesSerializer, NoteShareSerializer

redis_db = redis.StrictRedis(host="localhost", db=r_db, port=redis_port)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


class FundooLabelCreate(GenericAPIView):
    serializer_class = LabelSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request: request for create label
        :return: smd response
        """
        try:
            data = json.loads(request.body)
            if not 'name' in data:
                logger.error("'name' field not present in label serializer"+' for %s', request.user)
                raise KeyError("'name' field not present in label serializer")
            user = request.user
            name = data['name']
            # name = request.data["name"]

            label = Label.objects.create(name=name, user_id=user.id)
            label.save()
            logger.info('user created Label saved in database'+' for %s', request.user)
            redis_db.hmset(str(user.id) + 'label', {label.pk: label.name})
            logger.info("user created label saved in redis cache."+' for %s', request.user)
            response = servicesnote.smd_response(success=True, message='You are successfully saved',
                                                 http_status=status.HTTP_201_CREATED)
        except (TypeError, KeyError, ValueError) as e:
            logger.info(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.info(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def get(self, request):
        """
        :param request: client request for get label
        :return: return required response
        """
        try:
            user_id = request.user.id
            user_redis_labels = redis_db.hvals(user_id)
            # print(user_redis_labels)
            if len(user_redis_labels) < 1:
                logger.info("Label are not present in redis cache"+' for %s', request.user)
                get_label = Label.objects.filter(user_id=user_id)
                logger.info("get all label form database"+' for %s', request.user)
                for x in range(len(get_label)):
                    # print(str(user_id) + 'label',
                    #       {get_label.values()[x]['id']: get_label.values()[x]['name']})
                    redis_db.hmset((str(user_id) + 'label'),
                                   {get_label.values()[x]['id']: get_label.values()[x]['name']})
                    logger.info("all labels insert into redis cache"+' for %s', request.user)
                user_redis_labels = redis_db.hvals(str(user_id) + 'label')

            response = servicesnote.smd_response(success=True, message='following is/are your label',
                                                 data=[user_label.decode('utf-8') for user_label in user_redis_labels],
                                                 http_status=status.HTTP_200_OK)
            logger.info("all labels of current user"+' for %s', request.user)
        except TypeError as e:
            logger.info(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.info(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
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
            user_id = request.user.id
            if redis_db.hexists(str(user_id) + 'label', label_id) != 0:
                label = redis_db.hget(str(user_id) + "label", label_id)
                logger.info("label fetched from redis cache"+' for %s', request.user)
                response = servicesnote.smd_response(success=True, message='your label is',
                                                     data=[label.decode('utf-8')],
                                                     http_status=status.HTTP_200_OK)

            elif Label.objects.filter(user_id=user_id, id=label_id).exists():
                label = Label.objects.get(id=label_id)
                redis_db.hmset(str(user_id) + 'label', {label_id: label})
                logger.info('fetching from label database and store in redis cache'+' for %s', request.user)
                response = servicesnote.smd_response(success=True, message='your label is',
                                                     data=[str(label)],
                                                     http_status=status.HTTP_200_OK)
            else:
                logger.error('label not present database'+' for %s', request.user)
                response = servicesnote.smd_response(message='label does exist',
                                                     http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
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
                response = servicesnote.smd_response(success=True, message='label is successfully deleted',
                                                     http_status=status.HTTP_204_NO_CONTENT)
                logger.info('requested label is successfully deleted'+' for %s', request.user)
            elif Label.objects.filter(user_id=request.user.id, id=label_id).exists():
                get_label = Label.objects.get(id=label_id, user_id=request.user.id)
                get_label.delete()
                response = servicesnote.smd_response(success=True, message='label is successfully deleted',
                                                     http_status=status.HTTP_204_NO_CONTENT)
                logger.info('requested label is successfully deleted'+' for %s', request.user)
            else:
                logger.error('label does not exist in database'+' for %s', request.user)
                response = servicesnote.smd_response(message='Label does not exist in database',
                                                     http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def put(self, request, label_id):
        """
        :param request: client request for delete label
        :param label_id: delete by label id
        :return: return response
        """

        try:
            put_serializer = LabelSerializer(data=request.data)
            if not 'name' in put_serializer.initial_data:
                logger.error("name field not exist in Label serializer"+' for %s', request.user)
                raise KeyError("name field not exist in Label serializer")
            if put_serializer.is_valid():
                user_id = request.user.id
                # if redis_db.hexists(str(user_id) + 'label', label_id) != 0:
                #     redis_db.hmset(str(user_id) + 'label', {label_id: put_serializer.data['name']})
                #     ############
                #     get_label = Label.objects.get(id=label_id, user_id=request.user.id)
                #     get_label.name = put_serializer.data['name']
                #     get_label.save()
                #     #######
                #     response = servicesnote.smd_response(success=True, message='your label is successfully update',
                #                                          http_status=status.HTTP_200_OK)
                #     logger.info("Label successfully updated"+' for %s', request.user)

                if Label.objects.filter(user_id=user_id, id=label_id).exists():
                    get_label = Label.objects.get(id=label_id, user_id=request.user.id)
                    get_label.name = put_serializer.data['name']
                    get_label.save()
                    redis_db.hmset(str(user_id) + 'label', {label_id: put_serializer.data['name']})
                    response = servicesnote.smd_response(success=True, message='Label successfully Updated',
                                                         http_satus=status.HTTP_200_OK)
                    logger.info("Label successfully updated"+' for %s', request.user)
                else:
                    logger.error('Label does not exist in database.'+' for %s', request.user)
                    response = servicesnote.smd_response(message='label not valid',
                                                         http_satus=status.HTTP_400_BAD_REQUEST)
            else:
                logger.error('Label serializer not valid'+' for %s', request.user)
                response = servicesnote.smd_response(message='label not valid',
                                                     http_satus=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response


# =====================================


class FundooNoteCreate(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request: user request for create fundoo note
        :return: smd response
        """
        try:
            note_data = NotesSerializer(data=request.data, partial=True)
            user = request.user
            global labels, collaborate, label_flag, collaborate_flag
            label_flag, collaborate_flag = False, False

            if len(note_data.initial_data) == 0:
                logger.error("field not present"+' for %s', request.user)
                raise KeyError('one field should be present')

            if 'label' in note_data.initial_data:
                labels = note_data.initial_data['label']
                label_flag = True
                # =====================================================
                xx = Label.objects.filter(name__in=[x for x in labels])
                if len(labels) == len(xx):
                    note_data.initial_data['label'] = [xx[b].id for b in range(len(xx))]
                else:
                    raise ValueError('Label name not found in Label model')
                # =====================================================

                # note_data.initial_data['label'] = [Label.objects.get(name=x).id
                #                                    if Label.objects.filter(name=x).exists()
                #                                    else "Label not exist" for x in labels]
            if 'collaborate' in note_data.initial_data:
                collaborate = note_data.initial_data['collaborate']
                collaborate_flag = True
                # ==========================================================
                yy = User.objects.filter(email__in=[x for x in collaborate])
                print(yy)
                if len(collaborate) == len(yy):
                    note_data.initial_data['collaborate'] = [yy[b].id for b in range(len(yy))]
                else:
                    raise ValueError("this email not present in database")

                # ==========================================================
                # note_data.initial_data['collaborate'] = [User.objects.get(email=x).id if
                #                                          User.objects.filter(email=x).exists() and
                #                                          x != User.objects.get(id=user.id).email
                #                                          else "For collaborate user not exist" for x in collaborate]

            # print(note_data.initial_data['collaborate'])
            if note_data.is_valid():
                saved_note_data = note_data.save(user_id=user.id)
                if label_flag:
                    note_data.initial_data['label'] = labels
                if collaborate_flag:
                    note_data.initial_data['collaborate'] = collaborate
                note_data.save()
                # print(note_data.initial_data)
                # print(note_data.data)
                redis_db.hmset(str(saved_note_data.user_id) + 'note', {saved_note_data.id: note_data.initial_data})

                response = servicesnote.smd_response(success=True, message='Your note is successfully created',
                                                     http_status=status.HTTP_201_CREATED)
                logger.info('Your note is successfully created'+' for %s', request.user)
            else:
                logger.error('Note serializer data not valid'+' for %s', request.user)
                response = servicesnote.smd_response(message='something is wrong',
                                                     data=['Please enter correct ' + str(
                                                         [x for x in note_data.errors.keys()])],
                                                     http_status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, ValueError, TypeError) as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def get(self, request):
        """
        :param request: user request for fetching all notes created by requested user
        :return: smd response
        """
        try:
            user_redis_note = redis_db.hvals(str(request.user.id) + 'note')
            logger.info("select user notes from redis cache"+' for %s', request.user)

            if len(user_redis_note) < 1:
                logger.info("No data found in redis cache"+' for %s', request.user)
                get_note = FundooNote.objects.filter(user_id=request.user.id)
                note_data = NotesSerializer(get_note, many=True)
                try:
                    for i in range(len(note_data.data)):
                        note_data.data[i]['label'] = [Label.objects.get(id=x).name
                                                      for x in note_data.data[i]['label']]
                        note_data.data[i]['collaborate'] = [User.objects.get(id=x).email
                                                            for x in note_data.data[i]['collaborate']]
                except Exception:
                    raise ValueError("some data not present in database")
                i = 0
                logger.info("insert notes into redis cache"+' for %s', request.user)
                for data in note_data.data:
                    # print({get_note.values()[i]['id']: [x for x in data.values()]})
                    redis_db.hmset(str(request.user.id) + 'note',
                                   {get_note.values()[i]['id']: {k: v for k, v in data.items()}})
                    i += 1

                user_redis_note = redis_db.hvals(str(request.user.id) + 'note')

            response = servicesnote.smd_response(success=True, message='following is your created note',
                                                 data=[user_note.decode('utf-8') for user_note in user_redis_note],
                                                 http_status=status.HTTP_200_OK)
        except (KeyError, ValueError, TypeError)as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
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
        try:
            user_redis_note = redis_db.hget(str(request.user.id) + 'note', note_id)
            logger.info("fetch data from redis cache"+' for %s', request.user)
            # print(user_redis_note)
            if user_redis_note is None:
                logger.info('data not present in redis cache'+' for %s', request.user)
                get_note = FundooNote.objects.filter(id=note_id, user_id=request.user.id)
                logger.info('fetch data from note serialize model'+' for %s', request.user)
                note_data = NotesSerializer(get_note, many=True)
                try:
                    if len(note_data.data) > 0:
                        note_data.data[0]['label'] = [Label.objects.get(id=x).name
                                                      for x in note_data.data[0]['label']]
                        note_data.data[0]['collaborate'] = [User.objects.get(id=x).email
                                                            for x in note_data.data[0]['collaborate']]
                except (ValueError, Exception) as e:
                    raise ValueError(e)
                user_redis_note = {k: v for k, v in note_data.data[0].items()}

                # print(get_note.values())
                logger.info('insert note data into redis cache'+' for %s', request.user)
                redis_db.hmset(str(get_note.values()[0]['user_id']) + 'note',
                               {get_note.values()[0]['id']: user_redis_note})

                response = servicesnote.smd_response(success=True, message='following is your note of given note id',
                                                     data=[user_redis_note],
                                                     http_status=status.HTTP_200_OK)
            else:
                response = servicesnote.smd_response(success=True, message='following is your note of given note id',
                                                     data=[user_redis_note.decode('utf-8')],
                                                     http_status=status.HTTP_200_OK)
        except ValueError as e:
            logger.error('database error'+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def delete(self, request, note_id):
        """
        :param request: request for delete the note created by authenticated user
        :param note_id: check credentials by note_id
        :return: return response
        """
        try:
            try:
                get_label = FundooNote.objects.get(id=note_id, user_id=request.user.id)
            except FundooNote.DoesNotExist as e:
                logger.error(str(e)+' for %s', request.user)
                raise ValueError(e)

            get_label.delete()
            redis_db.hdel(str(request.user.id) + 'note', note_id)
            response = servicesnote.smd_response(success=True, message='note is successfully deleted',
                                                 http_status=status.HTTP_204_NO_CONTENT)
            logger.info('Note deleted of respective id'+' for %s', request.user)
        except ValueError as e:
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def put(self, request, note_id):
        """
        :param request:  data is requested
        :param note_id:  note id
        :return: will fetch note id from database
        """
        try:
            # print(request.user.username)
            instance = FundooNote.objects.get(id=note_id)
            data = request.data
            request_label, request_collaborate = [], []
            is_label, is_collaborate = False, False
            if 'label' in request.data:
                is_label = True
                request_label = data['label']
                data["label"] = [Label.objects.get(name=name).id for name in request_label]
            if 'collaborate' in request.data:
                is_collaborate = True
                request_collaborate = data['collaborate']
                data["collaborate"] = [User.objects.get(email=email).id for email in request_collaborate]

            serializer = NotesSerializer(instance, data=data, partial=True)
            # here serialized data checked for validation and saved
            if serializer.is_valid():
                serializer.save()
                logger.info('Update in database'+' for %s', request.user)
                redis_note = redis_db.hget(str(request.user.id) + 'note', note_id)
                # we can check redis_note is none or not
                # ------------------ if redis_note is None---------------------
                if is_label:
                    serializer.initial_data['label'] = request_label
                if is_collaborate:
                    serializer.initial_data['collaborate'] = request_collaborate
                redis_note = ast.literal_eval(redis_note.decode('utf-8'))
                for key, val in serializer.initial_data.items():
                    redis_note[key] = val
                    redis_db.hmset(str(request.user.id) + 'note', {note_id: redis_note})

                # ----------------------- else ----------------------
                # # if data not present in redis then save new saved data from database
                # saved_note = dict(serializer.data)
                # try:
                #     saved_note['label'] = [Label.objects.get(id=y).name
                #                   for y in serializer.data['label']]
                #     saved_note['collaborate'] = [User.objects.get(id=y).email
                #                         for y in serializer.data['collaborate']]
                # except (ValueError, KeyError, TypeError) as e:
                #     # raise ValueError('Database fetching query error')
                #     raise ValueError(e)
                # redis_db.hmset(str(request.user.id) + 'note', {note_id: saved_data})

                logger.info('Update in redis cache'+' for %s', request.user)
                response = servicesnote.smd_response(success=True, message='note updated',
                                                     http_status=status.HTTP_200_OK)
            else:
                logger.error("data not valid serialized"+' for %s', request.user)
                response = servicesnote.smd_response(message='note was not update',
                                                     http_status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, KeyError, TypeError) as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e),
                                                 http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e),
                                                 http_status=status.HTTP_404_NOT_FOUND)
        return response


class HelloView(APIView):
    """
    This HelloView api is a sample api for simple an example
    """
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
            if not 'title' in note_data.initial_data or not 'content' in note_data.initial_data:
                logger.error("title/content field not present in Note serializer"+' for %s', request.user)
                raise KeyError('title/content field not present in Note serializer')
            # print(note_data.initial_data)
            if note_data.is_valid():
                context = {
                    'title': note_data.data['title'],
                    'content': note_data.data['content'],
                    'domain': request.build_absolute_uri
                }
                # pdb.set_trace()
                # response = servicesnote.smd_response(success=True, message='share your note successfully',
                #                                                      )
                #                          http_status=status.HTTP_201_CREATED)
                response = servicesnote.smd_response(success=True, message='share your note successfully',
                                                     http_status=status.HTTP_201_CREATED)
                # return render(request, 'home.html', context)
            else:
                response = servicesnote.smd_response(message='something is wrong', http_status=
                status.HTTP_400_BAD_REQUEST)
                logger.error('Note share serializer not valid'+' for %s', request.user)
        except (ValueError, TypeError, KeyError) as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e)+' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response
