
"""
//Iotree42 sensor Network

//purpose: for handling signals to trigger something
//used software: python3, django,
//for hardware: Debian-Server

//design by Sebastian Stadler
//on behalf of the university of munich.

//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
"""

from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from .fluxcon import DelInfluxAll
from .grafanacon import DelGrafaAll
from .mqttcon import DelMqttClient


# when a user is created a profile will be created to.
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# when a user changed his information's the profile will be changed two if so.
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(pre_delete, sender=User)
def user_delete(sender, instance, **kwargs):
    username = str(instance)
    del_flux_client = DelInfluxAll(username)
    del_flux_client.run()
    del_grafa_client = DelGrafaAll(username)
    del_grafa_client.run()
    del_mqtt_client = DelMqttClient(username)
    del_mqtt_client.deldel()
