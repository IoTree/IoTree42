from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='iot-home'),
    path('about/', views.about, name='iot-about'),
]
