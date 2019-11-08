"""
tests.py
TDD functionality for our userlogin module
"""
import json

import requests
from fundoo.url_settings import login_url, share_note_url, register_url, forgot_password_url, pass_reset_url

with open('templates/test_cases.json') as f:
    USER_DETAILS = json.load(f)


# pylint: disable=missing-function-docstring
class TestAPI:
    """
    in TestApi class we test login functionality,
    registration functionality and reset password functionality
    """

    # # login test cases
    def test_login1(self):
        """
        :return: return true if http response is HTTP_201_CREATED
        """
        response = requests.post(url=login_url, data=USER_DETAILS[0]["test_user1"])
        # response = requests.post(url='http://localhost:8000/login/', data=USER_DETAILS[0]["test_user1"])
        assert response.status_code == 201

    #
    def test_login2(self):
        """
        :return: return true if http response is HTTP_201_CREATED
        """
        response = requests.post(url=login_url, data=USER_DETAILS[0]["test_user2"])
        assert response.status_code == 201

    def test_login3(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=login_url, data=USER_DETAILS[0]["test_user3"])
        assert response.status_code == 400

    def test_login4(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=login_url, data=USER_DETAILS[0]["test_user4"])
        assert response.status_code == 400

    #
    # # registrations test cases
    def test_registration1(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        print(USER_DETAILS[1]["test_user1"])
        response = requests.post(url=register_url, data=USER_DETAILS[1]["test_user1"])
        assert response.status_code == 400

    def test_registration2(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        print(USER_DETAILS[1]["test_user2"])
        response = requests.post(url=register_url, data=USER_DETAILS[1]["test_user2"])
        assert response.status_code == 400

    def test_registration3(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        print(USER_DETAILS[1]["test_user3"])
        response = requests.post(url=register_url, data=USER_DETAILS[1]["test_user3"])
        assert response.status_code == 400

    def test_registration4(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        print(USER_DETAILS[1]["test_user4"])
        response = requests.post(url=register_url, data=USER_DETAILS[1]["test_user4"])
        assert response.status_code == 400

    def test_registration5(self):
        """
        :return: return true if http response is HTTP_201_CREATED
        """
        print(USER_DETAILS[1]["test_user5"])
        response = requests.post(url=register_url, data=USER_DETAILS[1]["test_user5"])
        assert response.status_code == 201

    # # reset password test cases
    def test_reset_password1(self):
        """
        :return: return true if http response is HTTP_201_CREATED
        """
        response = requests.post(url=pass_reset_url + USER_DETAILS[2]["token1"]['token'], data=USER_DETAILS[2]["test1"])
        print(USER_DETAILS[2]["token1"]['token'])
        assert response.status_code == 201

    def test_reset_password2(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=pass_reset_url + USER_DETAILS[2]["token2"]['token'], data=USER_DETAILS[2]["test2"])
        print(USER_DETAILS[2]["token2"]['token'])
        assert response.status_code == 400

    def test_reset_password3(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=pass_reset_url + USER_DETAILS[2]["token3"]['token'], data=USER_DETAILS[2]["test3"])
        print(USER_DETAILS[2]["token3"]['token'])
        assert response.status_code == 400

    def test_reset_password4(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=pass_reset_url + USER_DETAILS[2]["token3"]['token'], data=USER_DETAILS[2]["test4"])
        print(USER_DETAILS[2]["token4"]['token'])
        assert response.status_code == 400

        # file forgot password test cases
    def test_forgot_password1(self):
        """
        :return: return true if http response is OK
        """
        response = requests.post(url=forgot_password_url, data=USER_DETAILS[3]["test1"])
        print(USER_DETAILS[3]["test1"])
        assert response.status_code == 200

    def test_forgot_password2(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=forgot_password_url, data=USER_DETAILS[3]["test2"])
        print(USER_DETAILS[3]["test2"])
        assert response.status_code == 400

    def test_forgot_password3(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=forgot_password_url, data=USER_DETAILS[3]["test3"])
        print(USER_DETAILS[3]["test3"])
        assert response.status_code == 400

    def test_forgot_password4(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=forgot_password_url, data=USER_DETAILS[3]["test4"])
        print(USER_DETAILS[3]["test4"])
        assert response.status_code == 400

    # share note
    def test_note_share1(self):
        """
        :return: return true if http response is HTTP_201_CREATED
        """
        response = requests.post(url=share_note_url, data=USER_DETAILS[4]['test1'])
        print(USER_DETAILS[4]['test1'])
        assert response.status_code == 201

    def test_note_share2(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=share_note_url, data=USER_DETAILS[4]['test2'])
        print(USER_DETAILS[4]['test2'])
        assert response.status_code == 400

    def test_note_share3(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=share_note_url, data=USER_DETAILS[4]['test3'])
        print(USER_DETAILS[4]['test3'])
        assert response.status_code == 400

    def test_note_share4(self):
        """
        :return: return true if http response is HTTP_400_BAD_REQUEST
        """
        response = requests.post(url=share_note_url, data=USER_DETAILS[4]['test4'])
        print(USER_DETAILS[4]['test4'])
        assert response.status_code == 400


if __name__ == '__main__':
    TestAPI()
