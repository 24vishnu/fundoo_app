import json
import pdb

from decouple import config
from django.contrib.auth.models import User
from django.test import TestCase

from fundoonote.models import Label, FundooNote
from fundoonote.serializers import NotesSerializer

# with open('templates/test_cases.json') as f:
#     USER_DETAILS = json.load(f)

header1 = {
    'HTTP_AUTHORIZATION': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIj'
                          'oxNTczOTAxNzk4LCJqdGkiOiIxNmZkZjkwM2FjMTg0MjU1OTY1NDRmYjQ0NDEzZmIxYyIsInVzZXJfaWQ'
                          'iOjEzOH0.rhMa9wxMyBNmHzN7L7HaUMiOiOtRV762HYGwWcBG1Hc'
}


class TestNoteAPI(TestCase):
    fixtures = ['project_database']

    def test_get_notes(self):
        response = self.client.get(config('NOTE_URL'), **header1)
        self.assertEqual(response.status_code, 200)

    def test_delete_note1(self):
        url = config('NOTE_DELETE_URL') + 'asd/'
        response = self.client.delete(url, content_type='application/json', **header1)
        self.assertEqual(response.status_code, 404)

    def test_delete_note2(self):
        print(FundooNote.objects.filter(user_id=138).values())
        url = config('NOTE_DELETE_URL') + '2/'
        response = self.client.delete(url, content_type='application/json', **header1)
        print(FundooNote.objects.filter(user_id=138).values())
        self.assertEqual(response.status_code, 200)

    def test_get_note1(self):
        url = config('NOTE_DELETE_URL') + '2/'
        response = self.client.get(url, content_type='application/json', **header1)
        self.assertEqual(response.status_code, 200)

    def test_get_note2(self):
        url = config('NOTE_DELETE_URL') + '122/'
        response = self.client.get(url, content_type='application/json', **header1)
        self.assertEqual(response.status_code, 404)

    def test_post_notes(self):
        data = {
            "title": "note",
            "content": "This note created by test case",
            "label": [
                "hello"
                # "label10"
            ],
            "is_archive": 'true',
            "is_trashed": 'false',
            "collaborate": [
                # "vishnu23kumar@gmail.com",
                "nk90600@gmail.com"
                # "sachinjadhav0273@gmail.com"
            ]
        }
        print(FundooNote.objects.filter(user_id=138).values())
        # print(Label.objects.filter(user_id=138).values())
        response = self.client.post(config('NOTE_URL'), data, content_type='application/json', **header1)
        print(FundooNote.objects.filter(user_id=138).values())
        self.assertEqual(response.status_code, 201)

    def test_put_note(self):
        data = {
            "content": "This note created by test case",
            "collaborate": [
                "nk90600@gmail.com"
            ]
        }
        z = FundooNote.objects.filter(id=2)
        zz = NotesSerializer(z, many=True)
        print(zz.data)
        response = self.client.put(config('NOTE_DELETE_URL') + '2/', data, content_type='application/json', **header1)
        z = FundooNote.objects.filter(id=2)
        zz = NotesSerializer(z, many=True)
        print(zz.data)

        self.assertEqual(response.status_code, 200)

    def test_archive_view1(self):
        response = self.client.get(config('ARCHIVE_URL'), **header1)
        self.assertEqual(response.status_code, 200)

    def test_trashed_view1(self):
        response = self.client.get(config('TRASHED_URL'), **header1)
        self.assertEqual(response.status_code, 200)

    def test_reminder_view1(self):
        response = self.client.get(config('REMINDER_URL'), **header1)
        self.assertEqual(response.status_code, 200)


class TestLableAPI(TestCase):
    fixtures = ['project_database']

    def test_magic_str(self):
        entry = Label(name="testing label")
        self.assertEqual(str(entry), entry.name)

    def test_get_labels(self):
        response = self.client.get(config('LABEL_URL'), **header1)
        self.assertEqual(response.status_code, 200)

    def test_post_labels(self):
        data = {'name': 'test_creation123'}
        print(Label.objects.filter(id=4).values())
        response = self.client.post(config('LABEL_URL'), data=data, **header1)
        self.assertEqual(response.status_code, 201)

    def test_delete_label(self):
        url = config('LABEL_DELETE_URL') + '4/'
        print(Label.objects.filter(user_id=138).values())
        response = self.client.delete(url, **header1)
        print(Label.objects.filter(user_id=138).values())
        self.assertEqual(response.status_code, 200)

    def test_put_label(self):
        url = config('LABEL_DELETE_URL') + '4/'
        print(Label.objects.filter(user_id=138).values())
        data = {'name': 'chenge by test case'}
        response = self.client.put(url, data=data, content_type='application/json', **header1)
        print(Label.objects.filter(user_id=138).values())
        self.assertEqual(response.status_code, 200)

    def test_get_label(self):
        url = config('LABEL_DELETE_URL') + '4/'
        print(Label.objects.filter(user_id=138).values())
        print(User.objects.all().values())
        response = self.client.get(url, **header1)
        self.assertEqual(response.status_code, 200)

#
# if __name__ == '__main__':
#     pass
