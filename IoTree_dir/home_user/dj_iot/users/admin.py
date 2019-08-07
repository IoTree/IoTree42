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

# to display all the content stored in Profile model on the admin site
admin.site.register(Profile)
