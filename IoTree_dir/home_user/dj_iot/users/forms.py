
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
from .mango import MongoCon
from captcha.fields import CaptchaField
import datetime


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
    first_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data['first_name']
        if commit:
            print(user.first_name)
            user.save()
        return user


# class for updating user fields
class UserUpdateForm(UniqueEmailForm, forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField(label="Mqtt Username", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    first_name = forms.CharField(label="Mqtt Password", widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name']
        labels = {
            'username': ['mqtt_username']
        }


# class for updating the profile
class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image']


# class for making a gateway choice field with all the gateways related to the username
class IDPostForm(forms.Form):
    gateway_id = forms.ChoiceField(choices=[("no data", "No Data")])

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(IDPostForm, self).__init__(*args, **kwargs)
        gateways = MongoCon(user)
        self.choices = gateways.find_gateways()
        if not self.choices:
            self.fields['gateway_id'].choices = [('no data', 'No Data')]
        else:
            self.fields['gateway_id'].choices = self.choices


# class for making fields for the inquiry page
class InquiryPostForm(forms.Form):
    tree_branch = forms.CharField(max_length=120, required=False, label="Tree branch:  example(feather,tsl2591,...")
    in_order = forms.BooleanField(required=False, initial=True, label="In Order")
    negated = forms.BooleanField(required=False, initial=False, label="Negated")
    time_start = forms.SplitDateTimeField(required=False, initial=datetime.datetime(1970, 1, 1))
    time_end = forms.SplitDateTimeField(required=False)
    filters = forms.ChoiceField(choices=[("data", "All Data"), ("tree", "Tree Branches")], label="Return all data or just the branches.")
