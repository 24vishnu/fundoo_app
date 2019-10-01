"""
short_url.py
message : short url file is compress length of url,
        here we use bitly api connection for short the url

author : vishnu kumar
date    :   1/10/2019
"""

# pylint: disable=unused-wildcard-import
import os
from pathlib import *
from bitly_api import Connection
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
env_path = Path('.') / '.env'


def sort_url_method(given_url):
    """
    :param given_url: a large length url for convert to short length url
    :return: a new url which is short length
    """

    API_USER = os.getenv("SHORT_API_USER")
    API_KEY = os.getenv("SHORT_API_KEY")
    bitly = Connection(API_USER, API_KEY)
    response = bitly.shorten(given_url)
    message_short_url = response['url']

    return message_short_url
