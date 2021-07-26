"""
//Iotree42 sensor Network

//purpose: to display all the content stored in Profile model on the admin site
//used software: python3, django
//for hardware: Debian-Server

//design by Sebastian Stadler
//on behalf of the university of munich.

//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
"""

from django.contrib import admin
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .mqttcon import InitMqttClient
from .fluxcon import InitInfluxUser
from .grafanacon import InitGrafaUser


class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        qs = User.objects.filter(email=self.cleaned_data['email'])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.count():
            raise forms.ValidationError('That email address is already in use')
        else:
            return self.cleaned_data['email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        init_mqtt_client = InitMqttClient(self.cleaned_data['username'], self.cleaned_data['password1'])
        init_mqtt_client.run()
        init_flux_client = InitInfluxUser(self.cleaned_data['username'], self.cleaned_data['password1'])
        init_flux_client.run()
        init_grafa_client = InitGrafaUser(self.cleaned_data['username'], self.cleaned_data['password1'], self.cleaned_data['email'])
        init_grafa_client.run()
        del init_grafa_client
        del init_flux_client
        del init_mqtt_client
        if commit:
            user.save()
        return user


class UserAdmin(UserAdmin):
    add_form = UserCreateForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', ),
        }),
    )



# to display all the content stored in Profile model on the admin site
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
