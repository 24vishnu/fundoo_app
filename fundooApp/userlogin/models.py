"""
models.py
    class for define some model classes as requirement

author : vishnu kumar
date : 29/09/2019
"""
from django.db import models
from django.forms import forms


class Registration(models.Model):
    """
    user registration model class for Register new user
    """
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=50)

    if username == "" or email == "" or password == "":
        raise forms.ValidationError(" one of the above field is empty")

    def __str__(self):
        return self.email + 'is email of' + self.username

    def __repr__(self):
        return self.username + ' is added.'

    class Meta:
        """
        This is meta class for user registration
        """
        verbose_name = 'detail'
        verbose_name_plural = 'details '


class UserLogin(models.Model):
    """
    User Login model class for login with username and password
    """
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=50)

    def __str__(self):
        return "username {} password {}".format(self.username, self.password)

    class Meta:
        """
        This is meta class for user login
        """
        verbose_name = 'Authorization'
        verbose_name_plural = 'password authentication'


class ForgotPassword(models.Model):
    """
    Forgot password model class user send the password link on user provided email
    """
    email = models.EmailField(max_length=150)
    if email == "":
        raise forms.ValidationError(" email should not be empty!")

    def __str__(self):
        return "This is ForgotPassword class model of email : {} ".format(self.email)

    class Meta:
        """
        This is meta class for forgot password
        """
        verbose_name = 'emailAddress'


class PasswordReset(models.Model):
    """
     password reset model class used for set the new password of user with given user name
    """
    password1 = models.CharField(max_length=50)
    password2 = models.CharField(max_length=50)

    if password1 == "" or password2 == "":
        raise forms.ValidationError(" username/password should not be empty!")

    def __str__(self):
        return "new password is {} ".format(self.password1)

    class Meta:
        """
        This is meta class for password reset
        """
        verbose_name = 'password_reset'


class ImageUpload(models.Model):
    file_details = models.FileField(blank=False, null=False)

    def __str__(self):
        return str(self.file_details)
