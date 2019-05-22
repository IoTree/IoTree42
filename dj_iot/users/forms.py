from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class IDPostForm(forms.Form):
    gateways_id = forms.CharField(max_length=16, min_length=16)


class InquiryPostForm(forms.Form):
    gateway_id = forms.CharField(max_length=16, min_length=16, required=True)
    tree_branch = forms.CharField(max_length=120, required=False)
    # time_start = forms.DateTimeField()
    # time_end = forms.DateTimeField()
    filters = forms.ChoiceField(choices=[("tree", "Tree"), ("data", "Data")])
    in_order = forms.BooleanField(required=False, initial=True, label="In Order")
    negated = forms.BooleanField(required=False, initial=False, label="Negated")
