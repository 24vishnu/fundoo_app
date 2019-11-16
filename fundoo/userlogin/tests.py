import json

from decouple import config
from django.contrib.auth.models import User
from django.test import TestCase

with open('templates/test_cases.json') as f:
    USER_DETAILS = json.load(f)

header2 = {'Content/Type': 'application/json',
           'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InRlc3QiLCJwYXNzd29yZCI6'
                            'InRlc3RwYXNzd29yZCJ9.WQ2hluY8neVN2686SwVWitLuLvIsuocCd8G9_gKIVVo'
           }


class TestAPI(TestCase):
    """
    in TestApi class we test login functionality,
    registration functionality and reset password functionality
    """
    fixtures = ['project_database']

    # def test_registration1(self):
    #     """
    #     :return: return true if http response is HTTP_400_BAD_REQUEST
    #     """
    #     print(USER_DETAILS[1]["test_user1"])
    #     response = self.client.post(config('REGISTER_URL'), data=USER_DETAILS[1]["test_user1"])
    #     self.assertEqual(response.status_code, 201)
    #
    # def test_registration2(self):
    #     """
    #     :return: return true if http response is HTTP_400_BAD_REQUEST
    #     """
    #     print(USER_DETAILS[1]["test_user2"])
    #     response = self.client.post(config('REGISTER_URL'), data=USER_DETAILS[1]["test_user2"])
    #     self.assertEqual(response.status_code, 400)
    #
    # def test_registration3(self):
    #     """
    #     :return: return true if http response is HTTP_400_BAD_REQUEST
    #     """
    #     print(USER_DETAILS[1]["test_user3"])
    #     response = self.client.post(register_url, data=USER_DETAILS[1]["test_user3"])
    #     self.assertEqual(response.status_code, 400)
    #
    # def test_registration4(self):
    #     """
    #     :return: return true if http response is HTTP_400_BAD_REQUEST
    #     """
    #     print(USER_DETAILS[1]["test_user4"])
    #     response = self.client.post(config('REGISTER_URL'), data=USER_DETAILS[1]["test_user4"])
    #     self.assertEqual(response.status_code, 400)
    #
    # def test_registration(self):
    #     """
    #     :return: return true if http response is HTTP_201_CREATED
    #     """
    #     print(USER_DETAILS[1]["test_user5"])
    #     response = self.client.post(config('REGISTER_URL'), data=USER_DETAILS[1]["test_user5"])
    #     self.assertEqual(response.status_code, 201)

    # login test cases
    def test_login(self):
        """
        :return: return true if http response is HTTP_201_CREATED
        """
        print(User.objects.all())
        # User.objects.create_user(username='admin', password='admin')
        print(User.objects.all().values())
        response = self.client.post(config('LOGIN_URL'), data=USER_DETAILS[0]["test_user1"])
        print(USER_DETAILS[0]["test_user1"])
        self.assertEqual(response.status_code, 201)

    #
    # def test_login2(self):
    #     """
    #     :return: return true if http response is HTTP_201_CREATED
    #     """
    #     response = self.client.post(config('LOGIN_URL'), data=USER_DETAILS[0]["test_user2"])
    #     self.assertEqual(response.status_code, 201)
