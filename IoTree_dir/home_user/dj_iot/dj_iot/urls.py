"""dj_iot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from users import views as user_views
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('delete_user/', user_views.delete_user, name='delete-user'),
    path('treeview/', user_views.treeview, name='treeview'),
    path('setup_rpi/', user_views.setup_rpi, name='setup-rpi'),
    path('manual/', user_views.manual, name='manual'),
    path('tografana/', user_views.tografana, name='tografana'),
    re_path(r'^grafana/(?P<path>.*)$', user_views.GrafanaProxyView.as_view(), name='grafanaproxyview'),
    path('iotree_show/<str:tags>/<slug:time_start>/<slug:time_end>/', user_views.iotree_show, name='iotree-show'),
    path('iotree_download/<str:tags>/<slug:time_start>/<slug:time_end>/', user_views.iotree_download, name='iotree-download'),
    path('iotree_api/', user_views.iotree_api, name='iotree-api'),
    path('iotree_chart/<str:tags>/<slug:time_start>/<slug:time_end>/', user_views.iotree_chart, name='iotree-chart'),
    path('zip_download/<slug:version>/', user_views.zip_download, name='zip-download'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path('', include('iotdata.urls')),
    re_path(r'^captcha/', include('captcha.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
