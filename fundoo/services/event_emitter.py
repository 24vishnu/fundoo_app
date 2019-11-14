"""
event_emitter.py
EventEmitter provides multiple properties like on and emit. on property is used
to bind a function with the event and emit is used to fire an event

author : vishnu kumar
date : 1/10/2019
"""
import pdb
from email import message

from django.contrib.auth.models import User
from django.core import mail
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from pyee import BaseEventEmitter
from rest_framework import status
from rest_framework.reverse import reverse

from services import util

ee = BaseEventEmitter()


@ee.on('emptEvent')
def send_message(mail_subject, email, message_link):
    """
    :param mail_subject: subject of the email message
    :param email: this is receiver email address (HOST MAIL)
    :param message_link: message link is a message body in this parameter we
            add the a link for receiver
    :return: we return the status what is the status after sending mail (success or failed)
    """
    # pdb.set_trace()
    mail_message = EmailMessage(mail_subject, message_link, to=[email])
    status = mail_message.send()
    return status


@ee.on('messageEvent')
def temp_mail(subject, email, message_link):
    """
       :param subject: subject of the email message
       :param email: this is receiver email address (HOST MAIL)
       :param message_link: message link is a message body in this parameter we
               add the a link for receiver
       :return: we return the status what is the status after sending mail (success or failed)
       """
    # pdb.set_trace()
    user = User.objects.filter(email=email)
    if len(user) > 0:
        html_message = render_to_string('mail.html', {'message': message_link, 'user': user[0].username})
        message = mail.EmailMultiAlternatives(subject, html_message, to=[email])
        message.attach_alternative(html_message, 'text/html')
        message.send()
    else:
        response = util.smd_response(message='some thing is wrong',
                                     http_status=status.HTTP_400_BAD_REQUEST)
        return response

    # message.attach_file(image_file_name, 'image/png')
    # plain_message = strip_tags(html_message)
    # mail.send_mail(subject, plain_message, [], [email], html_message=html_message)
    # return HttpResponse("Done")
