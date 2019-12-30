from time import sleep

from celery import shared_task
from django.core.mail import send_mail

# create my_reminder decorator
"""
    get all notes
    get all reminder notes from all notes before one minute
if reminder note then send note email and true
else
send None email and false
"""

@shared_task
def send_mail_task(): # (remaining_time, recipient_list):
    # sleepy(remaining_time - (5*60*60*1000))
    # get all notes
    # get all reminder notes from all notes before one minute
    # sleep(1 minute)
    # call send_mail()

    sleep(15)
    send_mail('Reminder Notification',
              'Hi fundoo user your reminder is going to expire after five minutes',
              'udal1010singh@gmail.com',
              ['faxalav986@qmail2.net'])
              # recipient_list)
    return None