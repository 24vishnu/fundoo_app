import os
from dotenv import load_dotenv, find_dotenv
from pathlib import *

load_dotenv(find_dotenv())
env_path = Path('.') / '.env'


login_url = os.getenv('LOGIN_URL')
register_url = os.getenv('REGISTER_URL')
forgot_password_url = os.getenv('FORGOT_PASSWORD_URL')
pass_reset_url = os.getenv('PASSWORD_RESET_URL')
share_note_url = os.getenv('SHARE_NOTE_URL')