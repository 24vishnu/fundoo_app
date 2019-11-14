import json

import requests
from fundoo.settings import login_url

with open('templates/test_cases.json') as f:
    USER_DETAILS = json.load(f)


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
        assert response.status_code == 201
