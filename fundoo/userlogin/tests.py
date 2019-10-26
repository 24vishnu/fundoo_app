"""
tests.py
TDD functionality for our userlogin module
"""
import os
import json
import requests

with open('templates/test_cases.json') as f:
    USER_DETAILS = json.load(f)


# pylint: disable=missing-function-docstring
class TestAPI:

    """
    in TestApi class we test login functionality,
    registration functionality and reset password functionality
    """
    login_url = os.getenv('LOGIN_URL')
    register_url = os.getenv('REGISTER_URL')
    forgot_password_url = os.getenv('FORGOT_PASSWORD_URL')
    pass_reset_url = os.getenv('PASSWORD_RESET_URL')
    share_note_url = os.getenv('SHARE_NOTE_URL')
#     # login test cases
#     def test_login1(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.login_url, data=USER_DETAILS[0]["test_user1"])
#         assert response.status_code == 200
#
#     def test_login2(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.login_url, data=USER_DETAILS[0]["test_user2"])
#         assert response.status_code == 200
#
#     def test_login3(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.login_url, data=USER_DETAILS[0]["test_user3"])
#         assert response.status_code == 200
#
#     def test_login4(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.login_url, data=USER_DETAILS[0]["test_user4"])
#         assert response.status_code == 200
#
# # registrations test cases
#     def test_registration1(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.register_url, data=USER_DETAILS[1]["test_user1"])
#         assert response.status_code == 200
#
#     def test_registration2(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.register_url, data=USER_DETAILS[1]["test_user2"])
#         assert response.status_code == 200
#
#     def test_registration3(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.register_url, data=USER_DETAILS[1]["test_user3"])
#         assert response.status_code == 200
#
#     def test_registration4(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.register_url, data=USER_DETAILS[1]["test_user4"])
#         assert response.status_code == 200
#
# # reset password test cases
#     def test_reset_password1(self):
#         """
#         :return: return true if http response is METHOD_NOT_ALLOWED
#         """
#         response = requests.post(url=self.pass_reset_url, data=USER_DETAILS[2]["test1"])
#         assert response.status_code == 405
#
#     def test_reset_password2(self):
#         """
#         :return: return true if http response is METHOD_NOT_ALLOWED
#         """
#         response = requests.post(url=self.pass_reset_url, data=USER_DETAILS[2]["test2"])
#         assert response.status_code == 405
#
#     def test_reset_password3(self):
#         """
#         :return: return true if http response is METHOD_NOT_ALLOWED
#         """
#         response = requests.post(url=self.pass_reset_url, data=USER_DETAILS[2]["test3"])
#         assert response.status_code == 405
#
#     def test_reset_password4(self):
#         """
#         :return: return true if http response is METHOD_NOT_ALLOWED
#         """
#         response = requests.post(url=self.pass_reset_url, data=USER_DETAILS[2]["test4"])
#         assert response.status_code == 405
#
# # file forgot password test cases
#     def test_forgot_password1(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.forgot_password_url, data=USER_DETAILS[3]["test1"])
#         assert response.status_code == 200
#
#     def test_forgot_password2(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.forgot_password_url, data=USER_DETAILS[3]["test2"])
#         assert response.status_code == 200
#
#     def test_forgot_password3(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.forgot_password_url, data=USER_DETAILS[3]["test3"])
#         assert response.status_code == 200
#
#     def test_forgot_password4(self):
#         """
#         :return: return true if http response is OK
#         """
#         response = requests.post(url=self.forgot_password_url, data=USER_DETAILS[3]["test4"])
#         assert response.status_code == 200

    # share note
    def test_note_share1(self):
        """
        :return: return true if http response is OK
        """
        response = requests.post(url=self.share_note_url, data=USER_DETAILS[4]['test1'])
        assert response.status_code == 200

    def test_note_share2(self):
        """
        :return: return true if http response is OK
        """
        response = requests.post(url=self.share_note_url, data=USER_DETAILS[4]['test2'])
        assert response.status_code == 200

    def test_note_share3(self):
        """
        :return: return true if http response is OK
        """
        response = requests.post(url=self.share_note_url, data=USER_DETAILS[4]['test3'])
        assert response.status_code == 200

    def test_note_share4(self):
        """
        :return: return true if http response is OK
        """
        response = requests.post(url=self.share_note_url, data=USER_DETAILS[4]['test4'])
        assert response.status_code == 200


if __name__ == '__main__':
    TestAPI()
