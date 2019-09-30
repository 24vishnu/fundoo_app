"""
Models.py class for define some model classes as requirement
"""
from django.db import models
from django.forms import forms


class Registration(models.Model):
    """ user registration model class for Register new user"""
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=50)

    if username == "" or email == "" or password == "":
        raise forms.ValidationError(" one of the above field is empty")

    def __str__(self):
        return "This is Registration class model of {} user".format(self.username)

    class Meta:
        """ This is meta class for user registration """
        verbose_name = 'detail'
        verbose_name_plural = 'details '


class UserLogin(models.Model):
    """ User Login model class for login with username and password"""
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=50)

    def __str__(self):
        return "This is Login class model of {} user".format(self.username)

    class Meta:
        """ This is meta class for user login """
        verbose_name = 'user authentication'
        verbose_name_plural = 'password authentication'


class ForgotPassword(models.Model):
    """ Forgot password model class user send the password link on user provided email """
    email = models.EmailField(max_length=150)
    if email == "":
        raise forms.ValidationError(" email should not be empty!")

    def __str__(self):
        return "This is ForgotPassword class model of email : {} ".format(self.email)

    class Meta:
        """ This is meta class for forgot password """
        verbose_name = 'emailAddress'


class PasswordReset(models.Model):
    """ password reset model class used for set the new password of user with given user name"""
    username = models.CharField(max_length=50)
    password1 = models.CharField(max_length=50)
    password2 = models.CharField(max_length=50)

    if username == "" or password1 == "" or password2 == "":
        raise forms.ValidationError(" username/password should not be empty!")

    def __str__(self):
        return "This is PasswordReset class model of {} user".format(self.username)

    class Meta:
        """ This is meta class for password reset"""
        verbose_name = 'password_reset'