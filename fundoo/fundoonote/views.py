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
import logging
import pdb
import pickle

import redis
from dateutil.parser import parse
from decouple import config
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from elasticsearch_dsl import Q
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from fundoo.settings import file_handler, r_db, redis_port
from services import util as servicesnote, note
from services.event_emitter import ee
from services.pagination import PageLimitOffsetPagination
from .documents import NotesDocument
from .models import Label, FundooNote
from .serializers import LabelSerializer, NotesSerializer, NoteShareSerializer, NoteElasticsearchSerializer

redis_db = redis.StrictRedis(host="localhost", db=r_db, port=redis_port)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# ========================= USE CELERY =====================
from .tasks import send_mail_task


def index(request):
    # sleepy(10)
    send_mail_task.delay()
    return HttpResponse('<h1 style="color:red">Email has been send!!</h1>')


# ==========================================================

class LabelList(GenericAPIView):
    serializer_class = LabelSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: client request for get label
        :return: return required response
        """
        try:

            user_id = request.user.id
            print(user_id)
            user_redis_labels = redis_db.hgetall((str(user_id) + 'label'))
            if len(user_redis_labels) < 1:
                logger.info("Label are not present in redis cache" + ' for %s', request.user)
                get_label = Label.objects.filter(user_id=user_id)
                labels_list = [{'id': i.id, 'name': i.name} for i in get_label]

                logger.info("get all label form database" + ' for %s', request.user)
                # redis_db.hmset((str(user_id) + 'label'), labels_list)
                for x in range(len(labels_list)):
                    redis_db.hmset((str(user_id) + 'label'),
                                   {labels_list[x]['id']: labels_list[x]['name']})
                logger.info("all labels insert into redis cache" + ' for %s', request.user)
                user_redis_labels = redis_db.hgetall(str(user_id) + 'label')
                print(type(user_redis_labels))
            response = servicesnote.smd_response(success=True, message='following is/are your labels',
                                                 data=[{'id': label_key.decode('utf-8'),
                                                        'name': lable_value.decode('utf-8')}
                                                       for label_key, lable_value in user_redis_labels.items()],
                                                 http_status=status.HTTP_200_OK)
            logger.info("all labels of current user" + ' for %s', request.user)
        except TypeError as e:
            logger.info(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.info(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

    def post(self, request):
        """
        :param request: request for create label
        :return: smd response
        """

        try:
            print(request.user.id)
            serialised_label = LabelSerializer(data=request.data)
            if not 'name' in serialised_label.initial_data:
                logger.error("'name' field not present in label serializer" + ' for %s', request.user)
                raise KeyError("'name' field not present in label serializer")
            if serialised_label.is_valid():
                label_record = serialised_label.save(user_id=request.user.id)
                logger.info('user created Label saved in database' + ' for %s', request.user)
                redis_db.hmset(str(request.user.id) + 'label', {label_record.id: label_record.name})
                logger.info("user created label saved in redis cache." + ' for %s', request.user)
                response = servicesnote.smd_response(success=True, message='You are successfully saved',
                                                     data=Label.objects.filter(id=label_record.id).values()[0],
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


class LabelDetails(GenericAPIView):
    serializer_class = LabelSerializer

    permission_classes = (IsAuthenticated,)

    def get_objects(self, user, label_id):
        try:
            return Label.objects.get(id=label_id, user_id=user.id)
        except Label.DoesNotExist:
            logger.error('Label does not exist in database.' + ' for %s', user)
            raise Http404("Label does not exist")

    # @require_http_methods(["DELETE"])
    def delete(self, request, label_id):
        """
        :param request: client request for delete label
        :param label_id: delete by label id
        :return: return response
        """
        try:

            print("delete 2")
            result = redis_db.hdel(str(request.user.id) + 'label', label_id)
            if result != 0:
                get_label = self.get_objects(request.user, label_id)
                label_detail = {
                    'id': get_label.id,
                    'name': get_label.name
                }
                get_label.delete()
                logger.info('requested label is successfully deleted' + ' for %s', request.user)
            else:

                check_database = self.get_objects(request.user, label_id)
                label_detail = {
                    'id': check_database.id,
                    'name': check_database.name
                }
                print(check_database)
                check_database.delete()
                logger.info('requested label is successfully deleted' + ' for %s', request.user)
            response = servicesnote.smd_response(success=True, message='label is successfully deleted',
                                                 data=label_detail, http_status=status.HTTP_200_OK)
        except Http404 as e:
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
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
            print("put 3")
            put_serializer = LabelSerializer(data=request.data)
            if not 'name' in put_serializer.initial_data:
                logger.error("name field not exist in Label serializer" + ' for %s', request.user)
                raise KeyError("name field not exist in Label serializer")
            if put_serializer.is_valid():
                user_id = request.user.id
                label = self.get_objects(request.user, label_id)
                label.name = put_serializer.data['name']
                label_detail = {
                    'id': label.id,
                    'name': label.name
                }
                label.save()
                redis_db.hmset(str(user_id) + 'label', {label_id: put_serializer.data['name']})
                response = servicesnote.smd_response(success=True, message='Label successfully Updated',
                                                     data=label_detail, http_status=status.HTTP_200_OK)
                logger.info("Label successfully updated" + ' for %s', request.user)
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


class NoteList(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: user request for fetching all notes created by requested user
        :return: smd response
        """

        try:
            user_redis_note = note.write_through(request)
            all_notes = [x for x in user_redis_note if (not x['is_trashed']
                                                        and not x['is_archive'])]

            response = servicesnote.smd_response(success=True, message='following are your notes',
                                                 data=all_notes,
                                                 http_status=status.HTTP_200_OK)
            logger.info('Archive notes are received' + ' for %s', request.user)
        except (KeyError, ValueError, TypeError)as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     logger.error(str(e) + ' for %s', request.user)
        #     response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response

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
            if note_data.is_valid():
                saved_note_data = note_data.save(user_id=user.id)
                note_details = FundooNote.objects.filter(id=saved_note_data.id)
                note_details = note_details.values()[0]
                # todo if reminder is present then celery reminder task and add this note in queue for send mail
                if label_flag:
                    note_details['label'] = labels
                else:
                    note_details['label'] = []
                if collaborate_flag:
                    note_details['collaborate'] = collaborate
                    # ---------------------- >>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    if (len(note_details['collaborate']) > 0):
                        # note_link = request.build_absolute_uri(reverse('fundoonote:note_list'))
                        note_link = config('FRONT_DASHBOARD')
                        ee.emit('collaborateEvent', note_details['title'], note_details['collaborate'],
                                note_link, User.objects.get(id=request.user.id).username)
                    # ---------------------- >>>>>>>>>>>>>>>>>>>>>>>>>>>>
                else:
                    note_details['collaborate'] = []

                redis_db.hmset(str(saved_note_data.user_id) + 'note',
                               {saved_note_data.id: pickle.dumps({k: v for k, v in note_details.items()})})

                response = servicesnote.smd_response(success=True, message='Your note is successfully created',
                                                     data=note_details, http_status=status.HTTP_201_CREATED)
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
        print("test")
        return response


class NoteDetails(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = (IsAuthenticated,)

    def get_objects(self, user, label_id):
        try:
            return FundooNote.objects.get(id=label_id, user_id=user.id)
        except Label.DoesNotExist:
            raise Http404('Note does not exist!')

    def get(self, request, note_id):
        """
        :param note_id: get note using note id
        :param request: user request for fetching all notes created by requested user
        :return: smd response
        """
        try:
            user_redis_note = redis_db.hget(str(request.user.id) + 'note', note_id)
            logger.info("fetch data from redis cache" + ' for %s', request.user)

            if user_redis_note is None:
                logger.info('data not present in redis cache' + ' for %s', request.user)
                get_note = self.get_objects(request.user, note_id)
                # if len(get_note) == 0:
                #     raise ValueError('Id details not present in your database')
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
                               {get_note.values()[0]['id']: pickle.dumps(user_redis_note)})

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
            get_note = self.get_objects(request.user, note_id)
            if get_note is not None:
                note_detail = {
                    'id': get_note.id,
                    'title': get_note.title
                }
                get_note.delete()
                redis_db.hdel(str(request.user.id) + 'note', note_id)
                response = servicesnote.smd_response(success=True, message='note is successfully deleted',
                                                     data=note_detail, http_status=status.HTTP_200_OK)
                logger.info('Note deleted of respective id' + ' for %s', request.user)
            else:
                response = servicesnote.smd_response(message='no content',
                                                     http_status=status.HTTP_204_NO_CONTENT)
                logger.info('content not present ' + ' for %s', request.user)
        except (ValueError, Exception) as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        return response

    def put(self, request, note_id):
        """
        :param request:  data is requested
        :param note_id:  note id
        :return: will fetch note id from database
        """
        # todo if reminder is present then celery reminder task and add this note in queue for send mail

        try:
            # ==========================
            user_note = pickle.loads(redis_db.hget(str(request.user.id) + 'note', note_id))
            # ==========================

            instance = self.get_objects(request.user, note_id)
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

            if len(serializer.initial_data) == 0:
                logger.error("field not present" + ' for %s', request.user)
                raise KeyError('field Already upto date')
            if serializer.is_valid():
                new_details = serializer.save()
                new_details = FundooNote.objects.filter(id=new_details.id)
                image_url = NotesSerializer(new_details, many=True)
                updated_details = new_details.values()[0]
                print(image_url.data)

                updated_details['image'] = image_url.data[0]['image']
                logger.info('Update in database' + ' for %s', request.user)
                redis_note = redis_db.hget(str(request.user.id) + 'note', note_id)

                if is_label:
                    updated_details['label'] = request_label
                else:
                    updated_details['label'] = user_note['label']
                if is_collaborate:
                    updated_details['collaborate'] = request_collaborate
                    # ---------------------- >>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    new_collaborate = [usermail for usermail in  updated_details['collaborate']
                                       if usermail not in user_note['collaborate']]
                    if(len(new_collaborate) > 0):
                        # note_link = request.build_absolute_uri(reverse('fundoonote:note_list'))
                        note_link = config('FRONT_DASHBOARD')
                        ee.emit('collaborateEvent', updated_details['title'], new_collaborate,
                                note_link, User.objects.get(id=request.user.id).username)
                    # ---------------------- >>>>>>>>>>>>>>>>>>>>>>>>>>>>
                else:
                    updated_details['collaborate'] = user_note['collaborate']

                redis_note = pickle.loads(redis_note)
                for key, val in updated_details.items():
                    if key == 'reminder' or key == 'time_stamp':
                        redis_note[key] = str(val)
                    else:
                        redis_note[key] = val
                    redis_db.hmset(str(request.user.id) + 'note', {str(note_id): pickle.dumps(redis_note)})

                logger.info('Update in redis cache' + ' for %s', request.user)
                response = servicesnote.smd_response(success=True, message='note updated',
                                                     data=updated_details, http_status=status.HTTP_200_OK)
            else:
                logger.error("data not valid serialized" + ' for %s', request.user)
                response = servicesnote.smd_response(message='data not valid serialized',
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
                                                     data=context, http_status=status.HTTP_201_CREATED)
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

        user = request.user
        try:
            user_redis_note = note.write_through(request)
            # note_data = FundooNote.objects.filter(user_id=user.id)
            reminder_list = [reminder_note for reminder_note in user_redis_note if reminder_note['reminder']]
            # reminder_list = user_redis_note.values_list('reminder', flat=True)
            expire = []
            pending = []

            for rem_note in reminder_list:
                if rem_note['reminder'] == 'None' or rem_note['reminder'] is None:
                    continue
                elif timezone.now() > parse(rem_note['reminder']):
                    expire.append(rem_note)
                else:
                    pending.append(rem_note)

            # for i in range(len(reminder_list.values())):
            #     if reminder_list.values()[i]['reminder'] is None:
            #         continue
            #     elif timezone.now() > reminder_list.values()[i]['reminder']:
            #         expire.append(reminder_list.values()[i])
            #     else:
            #         pending.append(reminder_list.values()[i])
            reminder = {
                'fired': expire,
                'pending': pending
            }

            logger.info("Reminders data is loaded")
            return servicesnote.smd_response(message="Reminder data is:",
                                             data=reminder,
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
        try:
            user_redis_note = note.write_through(request)
            archived_note = [x for x in user_redis_note if (not x['is_trashed']
                                                            and x['is_archive'])]
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

            user_redis_note = note.write_through(request)

            trashed_note = [x for x in user_redis_note if x['is_trashed']]
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


class LabelNotesDetails(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, label_id):
        """
                :param request: user request for fetching all notes created by requested user
                :return: smd response
                """
        try:
            user_redis_note = note.write_through(request)
            label_name = Label.objects.get(id=label_id).name

            notes_of_label = [x for x in user_redis_note if label_name in x['label']]
            response = servicesnote.smd_response(success=True, message='following are all notes of given label',
                                                 data=notes_of_label,
                                                 http_status=status.HTTP_200_OK)
        except (KeyError, ValueError, TypeError)as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response


class ElasticSearchAPI(GenericAPIView):
    serializer_class = NoteElasticsearchSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, query_data):
        """
                :param request: user request for fetching all notes created by requested user
                :return: searched result
                """
        try:
            search = NotesDocument.search()
            search_result = Q('multi_match', query=query_data, fields=['title', 'content'])
            # search_result = Q('match', content=query_data)
            note_data = search.query(search_result)

            searched_notes = NotesSerializer(note_data.to_queryset(), many=True)
            print(note_data)
            print(len(searched_notes.data))
            response = servicesnote.smd_response(success=True, message='following your searched result',
                                                 data=searched_notes.data,
                                                 http_status=status.HTTP_200_OK)
        except (KeyError, ValueError, TypeError)as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e) + ' for %s', request.user)
            response = servicesnote.smd_response(message=str(e), http_status=status.HTTP_404_NOT_FOUND)
        return response
