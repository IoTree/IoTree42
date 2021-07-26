
"""
//Iotree42 sensor Network

//purpose: making input fields and types
//used software: python3, django, python module datetime,
//for hardware: Debian-Server

//design by Sebastian Stadler
//on behalf of the university of munich.

//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
"""

from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from captcha.fields import CaptchaField
from django.core.validators import RegexValidator
import datetime



isalphavalidator = RegexValidator(r'^[0-9a-zA-Z]*$', message='name must be alphanumeric', code='Invalid name')
# class for checking if mail already exists
class UniqueEmailForm:
    def clean_email(self):
        qs = User.objects.filter(email=self.cleaned_data['email'])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.count():
            raise forms.ValidationError('That email address is already in use')
        else:
            return self.cleaned_data['email']


# class for creating all fields for the user
class UserRegisterForm(UniqueEmailForm, UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(validators=[isalphavalidator], max_length=20, required=True)
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


# class for updating user fields
class UserUpdateForm(UniqueEmailForm, forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    username = forms.CharField(label="Mqtt Username", widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = User
        fields = ['email', 'username']
        labels = {
            'username': ['mqtt_username']
        }


# class for updating the profile
class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image']


class TreePostForm(forms.Form):
    time_start = forms.DateTimeField(required=False, initial=datetime.datetime(1970, 1, 1))
    time_end = forms.DateTimeField(required=False)
    action = forms.ChoiceField(choices=[("table", "As Table"), ("download", "As CSV-File"), ("delete", "Delete Selected")], label="Action")


class InputPostForm(forms.Form):
    textbox = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":5, "cols":20}), label="")
