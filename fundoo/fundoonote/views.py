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

import redis
import pdb
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from fundoo import settings
from fundoo.settings import file_handler, r_db, redis_port
from services import util as servicesnote, note
from services.pagination import PageLimitOffsetPagination

from .models import Label, FundooNote
from .serializers import LabelSerializer, NotesSerializer, NoteShareSerializer

# import pdb

redis_db = redis.StrictRedis(host="localhost", db=r_db, port=redis_port)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

from services.event_emitter import temp_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render


class LabelCreate(GenericAPIView):
    serializer_class = LabelSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request: request for create label
        :return: smd response
        """
        try:
            # todo rename data (new)
            print(request.user.id)
            serialised_label = LabelSerializer(data=request.data)
            if not 'name' in serialised_label.initial_data:
                logger.error("'name' field not present in label serializer" + ' for %s', request.user)
                raise KeyError("'name' field not present in label serializer")

            # pdb.set_trace()
            if serialised_label.is_valid():
                label_record = serialised_label.save(user_id=request.user.id)
                logger.info('user created Label saved in database' + ' for %s', request.user)
                redis_db.hmset(str(request.user.id) + 'label', {label_record.id: label_record.name})
                logger.info("user created label saved in redis cache." + ' for %s', request.user)
                response = servicesnote.smd_response(success=True, message='You are successfully saved',
                                                     http_status=status.HTTP_201_CREATED)
            else:
                response = servicesnote.smd_response(message='serializer not valid',
                                                     http_status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, KeyError, ValueError) as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def get(self, request):
        """
        :param request: client request for get label
        :return: return required response
        """
        try:
            user_id = request.user.id
            user_redis_labels = redis_db.hgetall((str(user_id) + 'label'))
            if len(user_redis_labels) < 1:
                logger.info("Label are not present in redis cache" + ' for %s', request.user)
                get_label = Label.objects.filter(user_id=user_id)
                logger.info("get all label form database" + ' for %s', request.user)
                for x in range(len(get_label)):
                    redis_db.hmset((str(user_id) + 'label'),
                                   {get_label.values()[x]['id']: get_label.values()[x]['name']})
                    logger.info("all labels insert into redis cache" + ' for %s', request.user)
                user_redis_labels = redis_db.hgetall(str(user_id) + 'label')
                print(type(user_redis_labels))
            response = servicesnote.smd_response(success=True, message='following is/are your labels',
                                                 data=[{label_key.decode('utf-8'): lable_value.decode('utf-8')}
                                                       for label_key, lable_value in user_redis_labels.items()],
                                                 # data=[user_redis_labels],
                                                 http_status=status.HTTP_200_OK)
            logger.info("all labels of current user" + ' for %s', request.user)
        except TypeError as e:
            logger.info(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.info(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response


class LabelDelete(GenericAPIView):
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
                logger.info("label fetched from redis cache" + ' for %s', request.user)
                response = servicesnote.smd_response(success=True, message='your label is',
                                                     data=[label.decode('utf-8')],
                                                     http_status=status.HTTP_200_OK)
            else:
                # pdb.set_trace()
                check_database = Label.objects.filter(user_id=user_id, id=label_id)
                if len(check_database) != 0:
                    redis_db.hmset(str(user_id) + 'label', {label_id: str({label_id: check_database[0]})})
                    logger.info('fetching from label database and store in redis cache' + ' for %s', request.user)
                    response = servicesnote.smd_response(success=True, message='your label is',
                                                         data=[str(check_database[0])],
                                                         http_status=status.HTTP_200_OK)
                else:
                    logger.error('label not present database' + ' for %s', request.user)
                    response = servicesnote.smd_response(message='label does exist',
                                                         http_status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def delete(self, request, label_id):
        """
        :param request: client request for delete label
        :param label_id: delete by label id
        :return: return response
        """
        try:
            result = redis_db.hdel(str(request.user.id) + 'label', label_id)
            if result != 0:
                get_label = Label.objects.get(id=label_id, user_id=request.user.id)
                get_label.delete()
                response = servicesnote.smd_response(success=True, message='label is successfully deleted',
                                                     http_status=status.HTTP_200_OK)
                logger.info('requested label is successfully deleted' + ' for %s', request.user)
            else:
                # pdb.set_trace()
                check_database = Label.objects.filter(id=label_id, user_id=request.user.id)
                if len(check_database) != 0:
                    print(check_database)
                    check_database[0].delete()
                    response = servicesnote.smd_response(success=True, message='label is successfully deleted',
                                                         http_status=status.HTTP_200_OK)
                    logger.info('requested label is successfully deleted' + ' for %s', request.user)
                else:
                    logger.error('label does not exist in database' + ' for %s', request.user)
                    response = servicesnote.smd_response(message='Label does not exist in database',
                                                         http_status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
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
                logger.error("name field not exist in Label serializer" + ' for %s', request.user)
                raise KeyError("name field not exist in Label serializer")
            if put_serializer.is_valid():
                user_id = request.user.id
                if Label.objects.filter(user_id=user_id, id=label_id).exists():
                    get_label = Label.objects.get(id=label_id, user_id=request.user.id)
                    get_label.name = put_serializer.data['name']
                    get_label.save()
                    redis_db.hmset(str(user_id) + 'label', {label_id: put_serializer.data['name']})
                    response = servicesnote.smd_response(success=True, message='Label successfully Updated',
                                                         http_status=status.HTTP_200_OK)
                    logger.info("Label successfully updated" + ' for %s', request.user)
                else:
                    logger.error('Label does not exist in database.' + ' for %s', request.user)
                    response = servicesnote.smd_response(message='label not valid',
                                                         http_status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.error('Label serializer not valid' + ' for %s', request.user)
                response = servicesnote.smd_response(message='label not valid',
                                                     http_status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response


class NoteCreate(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request: user request for create fundoo note
        :return: smd response
        """
        # pdb.set_trace()
        try:
            note_data = NotesSerializer(data=request.data, partial=True)

            user = request.user
            global labels, collaborate, label_flag, collaborate_flag
            label_flag, collaborate_flag = False, False
            # pdb.set_trace()
            if len(note_data.initial_data) == 0:
                logger.error("field not present" + ' for %s', request.user)
                raise KeyError('one field should be present')

            if 'label' in note_data.initial_data:
                labels = note_data.initial_data['label']
                label_flag = True
                # =====================================================
                filter_lables = Label.objects.filter(user_id=user.id, name__in=[x for x in labels])
                print(filter_lables)
                print(len(labels), len(filter_lables))
                if len(labels) == len(filter_lables):
                    note_data.initial_data['label'] = [filter_lables[b].id for b in range(len(filter_lables))]
                else:
                    raise ValueError('Label name not found in Label model')
            if 'collaborate' in note_data.initial_data:
                collaborate = note_data.initial_data['collaborate']
                collaborate_flag = True
                # ==========================================================
                collaborate_list = User.objects.filter(email__in=[x for x in collaborate])
                print(collaborate_list)
                if len(collaborate) == len(collaborate_list):
                    note_data.initial_data['collaborate'] = [collaborate_list[b].id for b in
                                                             range(len(collaborate_list))]
                else:
                    raise ValueError("this email not present in database")

            # pdb.set_trace()
            if note_data.is_valid():
                saved_note_data = note_data.save(user_id=user.id)
                if label_flag:
                    note_data.initial_data['label'] = labels
                if collaborate_flag:
                    note_data.initial_data['collaborate'] = collaborate

                redis_db.hmset(str(saved_note_data.user_id) + 'note',
                               {saved_note_data.id: str({k: v for k, v in note_data.initial_data.items()})})

                response = servicesnote.smd_response(success=True, message='Your note is successfully created',
                                                     http_status=status.HTTP_201_CREATED)
                logger.info('Your note is successfully created' + ' for %s', request.user)
            else:
                logger.error('Note serializer data not valid' + ' for %s', request.user)
                response = servicesnote.smd_response(message='something is wrong',
                                                     data=['Please enter correct ' + str(
                                                         [x for x in note_data.errors.keys()])],
                                                     http_status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, ValueError, TypeError) as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def get(self, request):
        """
        :param request: user request for fetching all notes created by requested user
        :return: smd response
        """
        try:
            user_redis_note = note.write_through(request)
            response = servicesnote.smd_response(success=True, message='following is your created note',
                                                 data=user_redis_note,
                                                 http_status=status.HTTP_200_OK)
        except (KeyError, ValueError, TypeError)as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response


class NoteModification(GenericAPIView):
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
            logger.info("fetch data from redis cache" + ' for %s', request.user)
            # pdb.set_trace()
            if user_redis_note is None:
                logger.info('data not present in redis cache' + ' for %s', request.user)
                get_note = FundooNote.objects.filter(id=note_id, user_id=request.user.id)
                if len(get_note) == 0:
                    raise ValueError('Id details not present in your database')
                logger.info('fetch data from note serialize model' + ' for %s', request.user)
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

                logger.info('insert note data into redis cache' + ' for %s', request.user)
                redis_db.hmset(str(get_note.values()[0]['user_id']) + 'note',
                               {get_note.values()[0]['id']: str(user_redis_note)})

                response = servicesnote.smd_response(success=True, message='following is your note of given note id',
                                                     data=[user_redis_note],
                                                     http_status=status.HTTP_200_OK)
            else:
                user_redis_note = ast.literal_eval(user_redis_note.decode('utf-8'))
                response = servicesnote.smd_response(success=True, message='following is your note of given note id',
                                                     data=[user_redis_note],
                                                     http_status=status.HTTP_200_OK)
        except ValueError as e:
            logger.error('database error' + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def delete(self, request, note_id):
        """
        :param request: request for delete the note created by authenticated user
        :param note_id: check credentials by note_id
        :return: return response
        """
        try:
            get_label = FundooNote.objects.filter(id=note_id, user_id=request.user.id)
            if len(get_label) != 0:
                get_label[0].delete()
                redis_db.hdel(str(request.user.id) + 'note', note_id)
                response = servicesnote.smd_response(success=True, message='note is successfully deleted',
                                                     http_status=status.HTTP_200_OK)
                logger.info('Note deleted of respective id' + ' for %s', request.user)
            else:
                response = servicesnote.smd_response(message='no content',
                                                     http_status=status.HTTP_204_NO_CONTENT)
                logger.info('content not present ' + ' for %s', request.user)
        except (ValueError, Exception) as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def put(self, request, note_id):
        """
        :param request:  data is requested
        :param note_id:  note id
        :return: will fetch note id from database
        """
        try:
            # pdb.set_trace()
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
            # pdb.set_trace()
            serializer = NotesSerializer(instance, data=data, partial=True)

            if len(serializer.initial_data) == 0:
                logger.error("field not present" + ' for %s', request.user)
                raise KeyError('field Already upto date')

            if serializer.is_valid():
                serializer.save()
                logger.info('Update in database' + ' for %s', request.user)
                redis_note = redis_db.hget(str(request.user.id) + 'note', note_id)

                if is_label:
                    serializer.initial_data['label'] = request_label
                if is_collaborate:
                    serializer.initial_data['collaborate'] = request_collaborate
                redis_note = ast.literal_eval(redis_note.decode('utf-8'))
                for key, val in serializer.initial_data.items():
                    redis_note[key] = val
                    redis_db.hmset(str(request.user.id) + 'note', {str(note_id): str(redis_note)})

                logger.info('Update in redis cache' + ' for %s', request.user)
                response = servicesnote.smd_response(success=True, message='note updated',
                                                     http_status=status.HTTP_200_OK)
            else:
                logger.error("data not valid serialized" + ' for %s', request.user)
                response = servicesnote.smd_response(message='note was not update',
                                                     http_status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, KeyError, TypeError) as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e),
                                                 http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
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

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request: request parameter use for get data of Note like note title and note content
        :return: if note is not empty then render on share page
        """

        try:
            note_data = NoteShareSerializer(data=request.data)
            if not 'title' in note_data.initial_data or not 'content' in note_data.initial_data:
                logger.error("title/content field not present in Note serializer" + ' for %s', request.user)
                raise KeyError('title/content field not present in Note serializer')
            # print(note_data.initial_data)
            if note_data.is_valid():
                context = {
                    'title': note_data.data['title'],
                    'content': note_data.data['content'],
                    'domain': request.build_absolute_uri
                }
                response = servicesnote.smd_response(success=True, message='share your note successfully',
                                                     http_status=status.HTTP_201_CREATED)
                # return render(request, 'Example')
            else:
                response = servicesnote.smd_response(message='something is wrong', http_status=
                status.HTTP_400_BAD_REQUEST)
                logger.error('Note share serializer not valid' + ' for %s', request.user)
        except (ValueError, TypeError, KeyError) as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response


class Reminders(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # pdb.set_trace()
        user = request.user
        try:
            # pdb.set_trace()
            note_data = FundooNote.objects.filter(user_id=user.id)
            reminder_list = note_data.values_list('reminder', flat=True)
            expire = []
            pending = []
            for i in range(len(reminder_list.values())):
                if reminder_list.values()[i]['reminder'] is None:
                    continue
                elif timezone.now() > reminder_list.values()[i]['reminder']:
                    expire.append(reminder_list.values()[i])
                else:
                    pending.append(reminder_list.values()[i])

            reminder = {
                'fired': expire,
                'pending': pending
            }
            # pdb.set_trace()
            logger.info("Reminders data is loaded")

            return servicesnote.smd_response(message="Reminder data is:",
                                             data={k: {i[j]['id']: i[j]['reminder'] for j in range(len(i))}
                                                   for k, i in reminder.items()},
                                             # data={i[0]['id']: i[0]['reminder'] for i in reminder.values()},
                                             http_status=status.HTTP_200_OK)
        except TypeError:
            logger.info("no reminder set")
            return servicesnote.smd_response(message="No reminder set",
                                             http_status=status.HTTP_200_OK)


class NoteArchive(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: user request for fetching all notes created by requested user
        :return: smd response
        """

        # pdb.set_trace()
        try:
            user_redis_note = note.write_through(request)
            archived_note = [x for x in user_redis_note if (not list(x.values())[0]['is_trashed']
                                                            and list(x.values())[0]['is_archive'])]
            response = servicesnote.smd_response(success=True, message='following is archived note',
                                                 data=archived_note,
                                                 http_status=status.HTTP_200_OK)
            logger.info('Archive notes are received' + ' for %s', request.user)
        except (KeyError, ValueError, TypeError)as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response


class NoteTrashed(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: user request for fetching all notes created by requested user
        :return: smd response
        """
        try:
            # pdb.set_trace()
            user_redis_note = note.write_through(request)
            trashed_note = [x for x in user_redis_note if list(x.values())[0]['is_trashed']]
            response = servicesnote.smd_response(success=True, message='following is trashed note',
                                                 data=trashed_note,
                                                 http_status=status.HTTP_200_OK)
        except (KeyError, ValueError, TypeError)as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response


class PaginationApiView(ListAPIView):
    serializer_class = NotesSerializer
    filter_backends = [OrderingFilter]
    pagination_class = PageLimitOffsetPagination

    def get_queryset(self):
        try:
            # queryset_list = FundooNote.objects.filter(user_id=self.request.user.id)
            queryset_list = FundooNote.objects.all()
            logger.info("pagination api")
            return queryset_list
        except (ValueError, KeyError, TypeError, Exception) as e:
            logger.error(e)
            return servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)


class PaginationAPI(GenericAPIView):
    serializer_class = NotesSerializer

    def get(self, request):
        number_list = FundooNote.objects.all()
        users = [number_list.values()[i] for i in range(len(number_list))]
        page = request.GET.get('page', 1)
        paginator = Paginator(users, 2)

        try:
            user = paginator.page(page)
        except PageNotAnInteger:
            user = paginator.page(1)
        except EmptyPage:
            user = paginator.page(paginator.num_pages)
        # return servicesnote.smd_response(message='Dekho Na', data=[x for x in user], http_status=status.HTTP_200_OK)
        return render(request, 'note_pagination.html', {'numbers': user})
