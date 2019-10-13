"""
tests.py
TDD functionality for our userlogin module
"""
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
    login_url = "http://localhost:8000/api/login/"
    register_url = "http://localhost:8000/api/signup/"
    forgot_password_url = "http://localhost:8000/api/forgot_password/"
    pass_reset_url = "http://localhost:8000/api/reset_password/"

# login test cases
    def test_login1(self):
        response = requests.post(url=self.login_url, data=USER_DETAILS[0]["test_user1"])
        assert response.status_code == 200

    def test_login2(self):
        response = requests.post(url=self.login_url, data=USER_DETAILS[0]["test_user2"])
        assert response.status_code == 200

    def test_login3(self):
        response = requests.post(url=self.login_url, data=USER_DETAILS[0]["test_user3"])
        assert response.status_code == 200

    def test_login4(self):
        response = requests.post(url=self.login_url, data=USER_DETAILS[0]["test_user4"])
        assert response.status_code == 200

# registrations test cases
    def test_registration1(self):
        response = requests.post(url=self.register_url, data=USER_DETAILS[1]["test_user1"])
        assert response.status_code == 200

    def test_registration2(self):
        response = requests.post(url=self.register_url, data=USER_DETAILS[1]["test_user2"])
        assert response.status_code == 200

    def test_registration3(self):
        response = requests.post(url=self.register_url, data=USER_DETAILS[1]["test_user3"])
        assert response.status_code == 200

    def test_registration4(self):
        response = requests.post(url=self.register_url, data=USER_DETAILS[1]["test_user4"])
        assert response.status_code == 200

# reset password test cases
    def test_reset_password1(self):
        response = requests.post(url=self.pass_reset_url, data=USER_DETAILS[2]["test1"])
        assert response.status_code == 405

    def test_reset_password2(self):
        response = requests.post(url=self.pass_reset_url, data=USER_DETAILS[2]["test2"])
        assert response.status_code == 405

    def test_reset_password3(self):
        response = requests.post(url=self.pass_reset_url, data=USER_DETAILS[2]["test3"])
        assert response.status_code == 405

    def test_reset_password4(self):
        response = requests.post(url=self.pass_reset_url, data=USER_DETAILS[2]["test4"])
        assert response.status_code == 405

# file forgot password test cases
    def test_forgot_password1(self):
        response = requests.post(url=self.forgot_password_url, data=USER_DETAILS[3]["test1"])
        assert response.status_code == 200

    def test_forgot_password2(self):
        response = requests.post(url=self.forgot_password_url, data=USER_DETAILS[3]["test2"])
        assert response.status_code == 200

    def test_forgot_password3(self):
        response = requests.post(url=self.forgot_password_url, data=USER_DETAILS[3]["test3"])
        assert response.status_code == 200

    def test_forgot_password4(self):
        response = requests.post(url=self.forgot_password_url, data=USER_DETAILS[3]["test4"])
        assert response.status_code == 200


if __name__ == '__main__':
    TestAPI()
